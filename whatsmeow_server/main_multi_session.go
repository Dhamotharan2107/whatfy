//go:build ignore

package main

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"

	"go.mau.fi/whatsmeow"
	"go.mau.fi/whatsmeow/proto/waE2E"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/proto"
	_ "modernc.org/sqlite"
)

// ── Multi-Tenant WhatsApp Session Manager ────────────────────────────────────────

type WhatsAppSession struct {
	Client        *whatsmeow.Client
	SessionID     string
	TenantID      int
	DeviceName    string
	Connected     bool
	LoggedIn      bool
	Store         sqlstore.DeviceStore
	Mode          string // "whatsmeow" or "cloud"
	PhoneNumID    string // for Meta Cloud API
	SessionDBPath string
}

type SessionManager struct {
	Sessions map[string]*WhatsAppSession // sessionID -> session
	mu       sync.RWMutex
	ctx      context.Context
	cancel   context.CancelFunc
}

var sessionManager *SessionManager

// Create a new session manager
func NewSessionManager() *SessionManager {
	ctx, cancel := context.WithCancel(context.Background())
	return &SessionManager{
		Sessions: make(map[string]*WhatsAppSession),
		ctx:      ctx,
		cancel:   cancel,
	}
}

// Get a session by sessionID
func (sm *SessionManager) GetSession(sessionID string) (*WhatsAppSession, bool) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()
	session, exists := sm.Sessions[sessionID]
	return session, exists
}

// Create a new session
func (sm *SessionManager) CreateSession(tenantID int, deviceName string, mode string) (*WhatsAppSession, error) {
	sessionID := generateSessionID()

	sm.mu.Lock()
	defer sm.mu.Unlock()

	session := &WhatsAppSession{
		SessionID:  sessionID,
		TenantID:   tenantID,
		DeviceName: deviceName,
		Mode:       mode,
		Connected:  false,
		LoggedIn:   false,
	}

	sm.Sessions[sessionID] = session
	return session, nil
}

// Connect a session (WhatsMeow QR)
func (sm *SessionManager) ConnectSession(session *WhatsAppSession) error {
	session.mu.Lock()
	defer session.mu.Unlock()

	if session.Connected {
		return fmt.Errorf("already connected")
	}

	var deviceStore sqlstore.DeviceStore
	var err error

	if session.Mode == "cloud" {
		// For Meta Cloud API, create a mock device store
		deviceStore = session.Store
	} else {
		// For WhatsMeow, create a per-tenant database
		session.SessionDBPath = fmt.Sprintf("store_%d_%s.db", session.TenantID, session.SessionID[:8])
		deviceStore, err = sqlstore.New(sm.ctx, "sqlite",
			fmt.Sprintf("file:%s?_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)",
				session.SessionDBPath), waLog.Stdout("DB_"+session.SessionID, "ERROR", true))
		if err != nil {
			return fmt.Errorf("failed to create session DB: %w", err)
		}
	}

	// Create device store
	freshDevice := deviceStore.NewDevice()
	session.Store = deviceStore

	session.Client = whatsmeow.NewClient(freshDevice, waLog.Noop)
	session.Client.AddEventHandler(func(evt interface{}) {
		sm.handleSessionEvent(session, evt)
	})

	// Connect based on mode
	if session.Mode == "cloud" {
		// Meta Cloud API connection
		return session.connectCloudAPI()
	} else {
		// WhatsMeow QR connection
		return session.connectWhatsMeow()
	}
}

func (session *WhatsAppSession) connectCloudAPI() error {
	accessToken := session.Client.Store.AccessToken
	if accessToken == "" {
		return fmt.Errorf("access token not set - use /api/session/cloud-connect endpoint")
	}

	// Set meta cloud client
	session.Client.Store.PhoneNumberID = session.PhoneNumID
	session.Client.Store.AccessToken = accessToken
	session.Client.Store.WABID = session.Client.Store.PhoneNumberID

	// Connect to WhatsApp
	if err := session.Client.Connect(); err != nil {
		return fmt.Errorf("cloud API connect failed: %w", err)
	}

	session.Connected = true
	session.LoggedIn = true

	fmt.Printf("Session %s (Cloud API): Connected to WhatsApp\n", session.SessionID)
	return nil
}

func (session *WhatsAppSession) connectWhatsMeow() error {
	// Get first device from store
	deviceStore, err := session.Store.GetFirstDevice(sm.ctx)
	if err != nil {
		return fmt.Errorf("failed to get device: %w", err)
	}

	session.Client = whatsmeow.NewClient(deviceStore, waLog.Noop)
	session.Client.AddEventHandler(func(evt interface{}) {
		sm.handleSessionEvent(session, evt)
	})

	// Connect to WhatsApp
	if err := session.Client.Connect(); err != nil {
		return fmt.Errorf("WhatsMeow connect failed: %w", err)
	}

	session.Connected = true

	// Check if already logged in
	if session.Client.Store.ID != nil {
		session.LoggedIn = true
		fmt.Printf("Session %s (WhatsMeow): Already logged in\n", session.SessionID)
	}

	return nil
}

// Handle events for a specific session
func (sm *SessionManager) handleSessionEvent(session *WhatsAppSession, evt interface{}) {
	switch v := evt.(type) {
	case *events.Message:
		text := extractText(v.Message)
		fmt.Printf("Session %s: Message from %s - %s\n", session.SessionID, v.Info.Sender.String(), text)

		// Forward to FastAPI webhook
		entry := map[string]interface{}{
			"session_id": session.SessionID,
			"tenant_id":  session.TenantID,
			"from":       v.Info.Chat.String(),
			"sender":     v.Info.Sender.String(),
			"message":    text,
			"time":       v.Info.Timestamp.Unix(),
			"type":       "text",
		}

		msgType, fileName, _ := detectMediaInfo(v.Message)
		if msgType != "text" {
			msgID := v.Info.ID
			if msgID == "" {
				msgID = fmt.Sprintf("%d", v.Info.Timestamp.Unix())
			}
			ext := filepath.Ext(fileName)
			uniqueName := msgID + ext
			os.MkdirAll("media", 0755)
			mediaBytes, dlErr := session.Client.DownloadAny(sm.ctx, v.Message)
			if dlErr == nil && len(mediaBytes) > 0 {
				savePath := filepath.Join("media", uniqueName)
				if os.WriteFile(savePath, mediaBytes, 0644) == nil {
					entry["type"] = msgType
					entry["mediaURL"] = "/media/" + uniqueName
					entry["fileName"] = fileName
					entry["fileSize"] = formatFileSize(len(mediaBytes))
				}
			}
		}

		go sm.forwardToFastAPI(entry)

	case *events.Disconnected:
		fmt.Printf("Session %s: Disconnected from WhatsApp\n", session.SessionID)
		session.Connected = false

		if session.Mode == "whatsmeow" {
			go func() {
				time.Sleep(3 * time.Second)
				if session.Client.Store.ID != nil && !session.Client.IsConnected() {
					fmt.Printf("Session %s: Attempting reconnect...\n", session.SessionID)
					if err := session.Client.Connect(); err != nil {
						fmt.Printf("Session %s: Reconnect failed: %v\n", session.SessionID, err)
					}
				}
			}()
		}

	case *events.LoggedOut:
		fmt.Printf("Session %s: Logged out from mobile device\n", session.SessionID)
		session.LoggedIn = false
		session.Connected = false

		// Swap client
		oldClient := session.Client
		freshDevice := session.Store.NewDevice()
		session.Client = whatsmeow.NewClient(freshDevice, waLog.Noop)
		session.Client.AddEventHandler(func(evt interface{}) {
			sm.handleSessionEvent(session, evt)
		})

		go func() {
			oldClient.Disconnect()
			time.Sleep(3 * time.Second)
			_ = oldClient.Store.Delete(sm.ctx)
			if nc, err := sqlstore.New(sm.ctx, "sqlite",
				fmt.Sprintf("file:%s?_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)",
					session.SessionDBPath), waLog.Stdout("DB_"+session.SessionID, "ERROR", true)); err == nil {
				session.Store = nc
			}
			fmt.Printf("Session %s: Session reset complete\n", session.SessionID)
		}()
	}
}

// Forward message to FastAPI webhook
func (sm *SessionManager) forwardToFastAPI(entry map[string]interface{}) {
	data, err := json.Marshal(entry)
	if err != nil {
		return
	}

	webhookURL := os.Getenv("FASTAPI_URL")
	if webhookURL == "" {
		webhookURL = "http://localhost:5000/wa/incoming"
	}

	hc := &http.Client{Timeout: 30 * time.Second}
	resp, err := hc.Post(webhookURL, "application/json", bytes.NewReader(data))
	if err != nil {
		fmt.Printf("Session %s: Webhook error: %v\n", entry["session_id"], err)
		return
	}
	resp.Body.Close()
}

// Disconnect a session
func (sm *SessionManager) DisconnectSession(sessionID string) error {
	session, exists := sm.GetSession(sessionID)
	if !exists {
		return fmt.Errorf("session not found")
	}

	session.mu.Lock()
	defer session.mu.Unlock()

	if session.Client.IsConnected() {
		session.Client.Disconnect()
	}

	if session.Mode == "whatsmeow" && session.SessionDBPath != "" {
		os.Remove(session.SessionDBPath)
	}

	sm.mu.Lock()
	delete(sm.Sessions, sessionID)
	sm.mu.Unlock()

	fmt.Printf("Session %s: Disconnected\n", sessionID)
	return nil
}

// Generate a unique session ID
func generateSessionID() string {
	b := make([]byte, 12)
	_, _ = rand.Read(b)
	return fmt.Sprintf("%x", b)[:12]
}

// ── Helper Functions ─────────────────────────────────────────────────────────────

func extractText(msg *waE2E.Message) string {
	if msg == nil {
		return ""
	}
	if t := msg.GetConversation(); t != "" {
		return t
	}
	if ext := msg.GetExtendedTextMessage(); ext != nil && ext.GetText() != "" {
		return ext.GetText()
	}
	if img := msg.GetImageMessage(); img != nil {
		if c := img.GetCaption(); c != "" {
			return "[Image] " + c
		}
		return "[Image]"
	}
	if vid := msg.GetVideoMessage(); vid != nil {
		if c := vid.GetCaption(); c != "" {
			return "[Video] " + c
		}
		return "[Video]"
	}
	if doc := msg.GetDocumentMessage(); doc != nil {
		if f := doc.GetFileName(); f != "" {
			return "[Document] " + f
		}
		return "[Document]"
	}
	if msg.GetAudioMessage() != nil {
		return "[Voice message]"
	}
	if msg.GetStickerMessage() != nil {
		return "[Sticker]"
	}
	return "[Message]"
}

func detectMediaInfo(msg *waE2E.Message) (msgType, fileName, mimeType string) {
	if msg == nil {
		return "text", "", ""
	}
	if img := msg.GetImageMessage(); img != nil {
		mime := img.GetMimetype()
		if mime == "" {
			mime = "image/jpeg"
		}
		return "image", "image" + mimeToExt(mime), mime
	}
	if vid := msg.GetVideoMessage(); vid != nil {
		mime := vid.GetMimetype()
		if mime == "" {
			mime = "video/mp4"
		}
		return "video", "video" + mimeToExt(mime), mime
	}
	if doc := msg.GetDocumentMessage(); doc != nil {
		mime := doc.GetMimetype()
		name := doc.GetFileName()
		if name == "" {
			if mime == "" {
				mime = "application/octet-stream"
			}
			name = "document" + mimeToExt(mime)
		}
		return "document", name, mime
	}
	if aud := msg.GetAudioMessage(); aud != nil {
		mime := aud.GetMimetype()
		if mime == "" {
			mime = "audio/ogg"
		}
		return "audio", "audio" + mimeToExt(mime), mime
	}
	if msg.GetStickerMessage() != nil {
		return "sticker", "sticker.webp", "image/webp"
	}
	return "text", "", ""
}

func mimeToExt(mime string) string {
	switch {
	case strings.HasPrefix(mime, "image/jpeg"):
		return ".jpg"
	case strings.HasPrefix(mime, "image/png"):
		return ".png"
	case strings.HasPrefix(mime, "image/gif"):
		return ".gif"
	case strings.HasPrefix(mime, "image/webp"):
		return ".webp"
	case strings.HasPrefix(mime, "video/mp4"):
		return ".mp4"
	case strings.HasPrefix(mime, "video/"):
		return ".mp4"
	case strings.HasPrefix(mime, "audio/ogg"):
		return ".ogg"
	case strings.HasPrefix(mime, "audio/mpeg"):
		return ".mp3"
	case strings.HasPrefix(mime, "audio/"):
		return ".m4a"
	case strings.HasPrefix(mime, "application/pdf"):
		return ".pdf"
	default:
		return ".bin"
	}
}

func formatFileSize(n int) string {
	if n < 1024 {
		return fmt.Sprintf("%d B", n)
	}
	if n < 1024*1024 {
		return fmt.Sprintf("%.1f KB", float64(n)/1024)
	}
	return fmt.Sprintf("%.1f MB", float64(n)/(1024*1024))
}

func parseJID(jidStr string) (types.JID, error) {
	if strings.Contains(jidStr, "@") {
		parts := strings.Split(jidStr, "@")
		if len(parts) == 2 {
			return types.NewJID(parts[0], parts[1]), nil
		}
	}
	return types.JID{}, fmt.Errorf("invalid JID format")
}

func normalizeNumber(n string) string {
	n = strings.ReplaceAll(n, " ", "")
	n = strings.ReplaceAll(n, "-", "")
	n = strings.ReplaceAll(n, "(", "")
	n = strings.ReplaceAll(n, ")", "")
	if !strings.HasPrefix(n, "+") {
		n = "+" + n
	}
	return n
}

func resolveRecipient(number string) (types.JID, error) {
	if strings.Contains(number, "@") {
		atIdx := strings.LastIndex(number, "@")
		user := strings.SplitN(number[:atIdx], ":", 2)[0]
		server := number[atIdx+1:]
		return types.NewJID(user, server), nil
	}
	return resolveNumberToJID(number)
}

func resolveNumberToJID(number string) (types.JID, error) {
	num := strings.TrimPrefix(normalizeNumber(number), "+")
	if len(num) < 7 {
		return types.JID{}, fmt.Errorf("invalid phone number")
	}
	results, err := sessionManager.GetSession(sessionManager.CurrentSessionID).Client.IsOnWhatsApp(sm.ctx, []string{num})
	if err == nil && len(results) > 0 && results[0].IsIn {
		return results[0].JID, nil
	}
	return types.NewJID(num, "s.whatsapp.net"), nil
}

// ── HTTP Server ────────────────────────────────────────────────────────────────

type HTTPServer struct {
	port string
}

func NewHTTPServer(port string) *HTTPServer {
	return &HTTPServer{port: port}
}

func (s *HTTPServer) Start() error {
	// Create session manager
	sessionManager = NewSessionManager()
	sessionManager.CurrentSessionID = "main"

	// Setup media directory
	os.MkdirAll("media", 0755)

	// Serve media files
	http.HandleFunc("/media/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		http.StripPrefix("/media/", http.FileServer(http.Dir("media"))).ServeHTTP(w, r)
	})

	// API Routes
	http.HandleFunc("/api/session/create", createSessionHandler)
	http.HandleFunc("/api/session/connect", connectSessionHandler)
	http.HandleFunc("/api/session/{sessionID}", getSessionHandler)
	http.HandleFunc("/api/sessions", listSessionsHandler)
	http.HandleFunc("/api/session/{sessionID}/disconnect", disconnectSessionHandler)
	http.HandleFunc("/api/session/{sessionID}/send", sendMessageHandler)
	http.HandleFunc("/api/session/{sessionID}/send-media", sendMediaHandler)
	http.HandleFunc("/api/session/{sessionID}/logout", logoutHandler)
	http.HandleFunc("/api/session/{sessionID}/status", sessionStatusHandler)
	http.HandleFunc("/api/session/{sessionID}/contacts", contactsHandler)

	// Public routes
	http.HandleFunc("/check", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok", "sessions": len(sessionManager.Sessions)})
	})

	addr := "0.0.0.0:" + s.port
	fmt.Printf("WhatsApp Multi-Session Server started on %s\n", addr)
	fmt.Printf("Running %d sessions\n", len(sessionManager.Sessions))

	return http.ListenAndServe(addr, nil)
}

// ── Request/Response Structures ───────────────────────────────────────────────────

type CreateSessionRequest struct {
	TenantID    int    `json:"tenant_id"`
	DeviceName  string `json:"device_name"`
	Mode        string `json:"mode"` // "whatsmeow" or "cloud"
	PhoneNumID  string `json:"phone_number_id,omitempty"`
	AccessToken string `json:"access_token,omitempty"`
}

type CreateSessionResponse struct {
	SessionID  string `json:"session_id"`
	DeviceName string `json:"device_name"`
	Mode       string `json:"mode"`
	Status     string `json:"status"`
}

type SessionStatusResponse struct {
	SessionID  string `json:"session_id"`
	TenantID   int    `json:"tenant_id"`
	DeviceName string `json:"device_name"`
	Connected  bool   `json:"connected"`
	LoggedIn   bool   `json:"logged_in"`
	Mode       string `json:"mode"`
	PhoneNumID string `json:"phone_number_id,omitempty"`
}

type ConnectSessionRequest struct {
	SessionID string `json:"session_id"`
}

type ConnectSessionResponse struct {
	SessionID string `json:"session_id"`
	Status    string `json:"status"`
	QRCode    string `json:"qr_code,omitempty"`
	Error     string `json:"error,omitempty"`
}

type SendMessageRequest struct {
	SessionID string `json:"session_id"`
	Number    string `json:"number"`
	Message   string `json:"message"`
}

type SendMediaRequest struct {
	SessionID string `json:"session_id"`
	Number    string `json:"number"`
	Caption   string `json:"caption"`
	File      string `json:"file"` // Base64 encoded
}

// ── HTTP Handlers ───────────────────────────────────────────────────────────────

func createSessionHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(map[string]string{"error": "method not allowed"})
		return
	}

	var req CreateSessionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": "invalid request body"})
		return
	}

	if req.Mode != "whatsmeow" && req.Mode != "cloud" {
		json.NewEncoder(w).Encode(map[string]string{"error": "invalid mode - must be 'whatsmeow' or 'cloud'"})
		return
	}

	if req.Mode == "cloud" && req.PhoneNumID == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "phone_number_id required for cloud mode"})
		return
	}

	if req.Mode == "cloud" && req.AccessToken == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "access_token required for cloud mode"})
		return
	}

	session, err := sessionManager.CreateSession(req.TenantID, req.DeviceName, req.Mode)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	if req.Mode == "cloud" {
		session.PhoneNumID = req.PhoneNumID
		session.AccessToken = req.AccessToken
		err = session.ConnectCloudAPI()
	}

	resp := CreateSessionResponse{
		SessionID:  session.SessionID,
		DeviceName: session.DeviceName,
		Mode:       session.Mode,
		Status:     "created",
	}

	json.NewEncoder(w).Encode(resp)
}

func connectSessionHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(map[string]string{"error": "method not allowed"})
		return
	}

	var req ConnectSessionRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": "invalid request body"})
		return
	}

	session, exists := sessionManager.GetSession(req.SessionID)
	if !exists {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not found"})
		return
	}

	err := sessionManager.ConnectSession(session)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	resp := ConnectSessionResponse{
		SessionID: session.SessionID,
		Status:    "connected",
	}

	// If WhatsMeow mode, get QR code
	if session.Mode == "whatsmeow" && !session.LoggedIn {
		resp.QRCode = "scan to connect"
	}

	json.NewEncoder(w).Encode(resp)
}

func getSessionHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	sessionID := strings.TrimPrefix(r.URL.Path, "/api/session/")
	if sessionID == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "session ID required"})
		return
	}

	session, exists := sessionManager.GetSession(sessionID)
	if !exists {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not found"})
		return
	}

	session.mu.RLock()
	defer session.mu.RUnlock()

	resp := SessionStatusResponse{
		SessionID:  session.SessionID,
		TenantID:   session.TenantID,
		DeviceName: session.DeviceName,
		Connected:  session.Connected,
		LoggedIn:   session.LoggedIn,
		Mode:       session.Mode,
		PhoneNumID: session.PhoneNumID,
	}

	json.NewEncoder(w).Encode(resp)
}

func listSessionsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	sessionManager.mu.RLock()
	defer sessionManager.mu.RUnlock()

	sessions := []SessionStatusResponse{}
	for _, session := range sessionManager.Sessions {
		session.mu.RLock()
		sessions = append(sessions, SessionStatusResponse{
			SessionID:  session.SessionID,
			TenantID:   session.TenantID,
			DeviceName: session.DeviceName,
			Connected:  session.Connected,
			LoggedIn:   session.LoggedIn,
			Mode:       session.Mode,
			PhoneNumID: session.PhoneNumID,
		})
		session.mu.RUnlock()
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"sessions": sessions,
		"total":    len(sessions),
	})
}

func disconnectSessionHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(map[string]string{"error": "method not allowed"})
		return
	}

	sessionID := strings.TrimPrefix(r.URL.Path, "/api/session/")
	if sessionID == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "session ID required"})
		return
	}

	err := sessionManager.DisconnectSession(sessionID)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(map[string]string{"status": "disconnected", "session_id": sessionID})
}

func sendMessageHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(map[string]string{"error": "method not allowed"})
		return
	}

	var req SendMessageRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": "invalid request body"})
		return
	}

	session, exists := sessionManager.GetSession(req.SessionID)
	if !exists {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not found"})
		return
	}

	session.mu.RLock()
	defer session.mu.RUnlock()

	if !session.Connected {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not connected"})
		return
	}

	jid, err := resolveRecipient(req.Number)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	msg := &waE2E.Message{Conversation: &req.Message}
	_, err = session.Client.SendMessage(sessionManager.ctx, jid, msg)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(map[string]string{
		"status":     "sent",
		"to":         jid.String(),
		"session_id": req.SessionID,
	})
}

func sendMediaHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		json.NewEncoder(w).Encode(map[string]string{"error": "method not allowed"})
		return
	}

	var req SendMediaRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": "invalid request body"})
		return
	}

	session, exists := sessionManager.GetSession(req.SessionID)
	if !exists {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not found"})
		return
	}

	session.mu.RLock()
	defer session.mu.RUnlock()

	if !session.Connected {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not connected"})
		return
	}

	jid, err := resolveRecipient(req.Number)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	// Decode base64 file
	fileData := []byte(req.File)
	data, err := base64.StdEncoding.DecodeString(string(fileData))
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": "failed to decode base64 file"})
		return
	}

	mimeType := http.DetectContentType(data)
	var msg *waE2E.Message

	if strings.HasPrefix(mimeType, "image/") {
		uploaded, err := session.Client.Upload(sessionManager.ctx, data, whatsmeow.MediaImage)
		if err != nil {
			json.NewEncoder(w).Encode(map[string]string{"error": "upload failed: " + err.Error()})
			return
		}
		msg = &waE2E.Message{
			ImageMessage: &waE2E.ImageMessage{
				Caption:       proto.String(req.Caption),
				URL:           proto.String(uploaded.URL),
				DirectPath:    proto.String(uploaded.DirectPath),
				MediaKey:      uploaded.MediaKey,
				Mimetype:      proto.String(mimeType),
				FileEncSHA256: uploaded.FileEncSHA256,
				FileSHA256:    uploaded.FileSHA256,
				FileLength:    proto.Uint64(uint64(len(data))),
			},
		}
	} else {
		uploaded, err := session.Client.Upload(sessionManager.ctx, data, whatsmeow.MediaDocument)
		if err != nil {
			json.NewEncoder(w).Encode(map[string]string{"error": "upload failed: " + err.Error()})
			return
		}
		msg = &waE2E.Message{
			DocumentMessage: &waE2E.DocumentMessage{
				Caption:       proto.String(req.Caption),
				URL:           proto.String(uploaded.URL),
				DirectPath:    proto.String(uploaded.DirectPath),
				MediaKey:      uploaded.MediaKey,
				Mimetype:      proto.String(mimeType),
				FileEncSHA256: uploaded.FileEncSHA256,
				FileSHA256:    uploaded.FileSHA256,
				FileLength:    proto.Uint64(uint64(len(data))),
				FileName:      proto.String("document"),
			},
		}
	}

	_, err = session.Client.SendMessage(sessionManager.ctx, jid, msg)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(map[string]string{
		"status":     "media sent",
		"to":         jid.String(),
		"session_id": req.SessionID,
	})
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	sessionID := strings.TrimPrefix(r.URL.Path, "/api/session/")
	if sessionID == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "session ID required"})
		return
	}

	session, exists := sessionManager.GetSession(sessionID)
	if !exists {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not found"})
		return
	}

	session.mu.Lock()
	if session.LoggedIn {
		session.LoggedIn = false
		session.Connected = false
		session.Client.Logout()
	}
	session.mu.Unlock()

	json.NewEncoder(w).Encode(map[string]string{
		"status":     "logged out",
		"session_id": sessionID,
	})
}

func sessionStatusHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	sessionID := strings.TrimPrefix(r.URL.Path, "/api/session/")
	if sessionID == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "session ID required"})
		return
	}

	session, exists := sessionManager.GetSession(sessionID)
	if !exists {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not found"})
		return
	}

	session.mu.RLock()
	defer session.mu.RUnlock()

	resp := map[string]interface{}{
		"session_id":      session.SessionID,
		"tenant_id":       session.TenantID,
		"device_name":     session.DeviceName,
		"connected":       session.Connected,
		"logged_in":       session.LoggedIn,
		"mode":            session.Mode,
		"phone_number_id": session.PhoneNumID,
	}

	json.NewEncoder(w).Encode(resp)
}

func contactsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	sessionID := strings.TrimPrefix(r.URL.Path, "/api/session/")
	if sessionID == "" {
		json.NewEncoder(w).Encode(map[string]string{"error": "session ID required"})
		return
	}

	session, exists := sessionManager.GetSession(sessionID)
	if !exists {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not found"})
		return
	}

	session.mu.RLock()
	defer session.mu.RUnlock()

	if !session.Connected {
		json.NewEncoder(w).Encode(map[string]string{"error": "session not connected"})
		return
	}

	contacts, err := session.Client.Store.Contacts.GetAllContacts(sessionManager.ctx)
	if err != nil {
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	list := []map[string]string{}
	for jid, contact := range contacts {
		list = append(list, map[string]string{
			"jid":  jid.String(),
			"name": contact.FullName,
		})
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"contacts": list,
	})
}

// ── Main ────────────────────────────────────────────────────────────────────────

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	server := NewHTTPServer(port)
	if err := server.Start(); err != nil {
		panic(err)
	}
}
