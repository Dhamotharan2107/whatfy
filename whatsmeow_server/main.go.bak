package main

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "os"
    "path/filepath"
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

var client    *whatsmeow.Client
var dbContainer *sqlstore.Container
var dbLog_     waLog.Logger
var clientLog_ waLog.Logger
var ctx = context.Background()
var incomingMessages []map[string]interface{}
var msgMu sync.Mutex

var sseClients = make(map[chan []byte]bool)
var sseMu sync.Mutex

var webhookURL = func() string {
	if v := os.Getenv("FASTAPI_URL"); v != "" {
		return v + "/wa/incoming"
	}
	return "http://localhost:5000/wa/incoming"
}()

func callWebhook(entry map[string]interface{}) {
    data, err := json.Marshal(entry)
    if err != nil {
        return
    }
    hc := &http.Client{Timeout: 30 * time.Second}
    resp, err := hc.Post(webhookURL, "application/json", bytes.NewReader(data))
    if err != nil {
        fmt.Println("Webhook error:", err)
        return
    }
    resp.Body.Close()
}

func broadcastSSE(data []byte) {
    sseMu.Lock()
    defer sseMu.Unlock()
    for ch := range sseClients {
        select {
        case ch <- data:
        default:
        }
    }
}

// extractText pulls the human-readable text out of any message type.
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
    if msg.GetReactionMessage() != nil {
        return "[Reaction]"
    }
    return "[Message]"
}

// detectMediaInfo returns (msgType, fileName, mimeType) for media messages.
// msgType is "image", "video", "document", "audio", "sticker", or "text".
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

// mimeToExt returns a file extension for a given MIME type.
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

// formatFileSize returns a human-readable file size string.
func formatFileSize(n int) string {
    if n < 1024 {
        return fmt.Sprintf("%d B", n)
    }
    if n < 1024*1024 {
        return fmt.Sprintf("%.1f KB", float64(n)/1024)
    }
    return fmt.Sprintf("%.1f MB", float64(n)/(1024*1024))
}

// normalizeNumber ensures number starts with + and has no spaces/dashes
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

func parseJID(jidStr string) (types.JID, error) {
    if strings.Contains(jidStr, "@") {
        parts := strings.Split(jidStr, "@")
        if len(parts) == 2 {
            return types.NewJID(parts[0], parts[1]), nil
        }
    }
    return types.JID{}, fmt.Errorf("invalid JID format")
}

// enableCORS adds necessary headers for local development
func enableCORS(w *http.ResponseWriter) {
    (*w).Header().Set("Access-Control-Allow-Origin", "*")
    (*w).Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
    (*w).Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
}

func eventHandler(evt interface{}) {
    switch v := evt.(type) {
    case *events.Message:
        text := extractText(v.Message)
        fmt.Printf("Message from: %s - %s\n", v.Info.Sender.String(), text)
        // Use Chat JID as reply-to (handles @lid privacy JIDs correctly)
        replyTo := v.Info.Chat.String()
        if replyTo == "" {
            replyTo = v.Info.Sender.String()
        }
        entry := map[string]interface{}{
            "from":    replyTo,
            "sender": v.Info.Sender.String(),
            "message": text,
            "time":    v.Info.Timestamp.Unix(),
            "type":    "text",
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
            mediaBytes, dlErr := client.DownloadAny(ctx, v.Message)
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

        msgMu.Lock()
        incomingMessages = append(incomingMessages, entry)
        msgMu.Unlock()
        if jsonData, marshalErr := json.Marshal(entry); marshalErr == nil {
            go broadcastSSE(jsonData)
        }
        // Forward to FastAPI for AI auto-reply (skip self-sent and group messages)
        if !v.Info.IsFromMe && v.Info.Chat.Server != "g.us" {
            go callWebhook(entry)
        }
    case *events.Disconnected:
        fmt.Println("Disconnected from WhatsApp")
        go func() {
            time.Sleep(3 * time.Second)
            // Only reconnect if the current global client still has a valid session
            if client.Store.ID != nil && !client.IsConnected() {
                fmt.Println("Attempting reconnect...")
                if err := client.Connect(); err != nil {
                    fmt.Println("Reconnect failed:", err)
                }
            }
        }()

    case *events.LoggedOut:
        // Fired when the user removes this session from WhatsApp mobile.
        // Swap client SYNCHRONOUSLY first so:
        //   1) statusHandler immediately returns loggedIn:false
        //   2) the Disconnected handler's 3s-sleep goroutine sees Store.ID==nil
        //      and skips the reconnect attempt
        fmt.Println("Logged out from mobile device, resetting session...")
        oldClient := client
        freshDevice := dbContainer.NewDevice()
        client = whatsmeow.NewClient(freshDevice, clientLog_)
        client.AddEventHandler(eventHandler)

        go func() {
            // Stop old client goroutines (prekey uploader, keepalive, etc.)
            // before touching its store, to avoid FK constraint failures.
            oldClient.Disconnect()
            time.Sleep(3 * time.Second)
            _ = oldClient.Store.Delete(ctx)

            // Reinit container so its device cache is fully cleared
            if nc, err := sqlstore.New(ctx, "sqlite",
                "file:store.db?_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)",
                dbLog_); err == nil {
                dbContainer = nc
            }
            fmt.Println("Session reset complete — ready to re-login")
        }()
    }
}

func newClient() {
    deviceStore, err := dbContainer.GetFirstDevice(ctx)
    if err != nil {
        panic(err)
    }
    client = whatsmeow.NewClient(deviceStore, clientLog_)
    client.AddEventHandler(eventHandler)
}

func main() {
    dbLog_ = waLog.Stdout("Database", "ERROR", true)
    clientLog_ = waLog.Noop

    var err error
    dbContainer, err = sqlstore.New(ctx, "sqlite", "file:store.db?_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)", dbLog_)
    if err != nil {
        os.Remove("store.db")
        dbContainer, err = sqlstore.New(ctx, "sqlite", "file:store.db?_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)", dbLog_)
        if err != nil {
            panic(err)
        }
    }

    newClient()

    // Auto-connect if already logged in
    if client.Store.ID != nil {
        if err := client.Connect(); err != nil {
            fmt.Println("Auto-connect error:", err)
        }
    }

    // Serve downloaded media files
    os.MkdirAll("media", 0755)
    http.HandleFunc("/media/", func(w http.ResponseWriter, r *http.Request) {
        enableCORS(&w)
        http.StripPrefix("/media/", http.FileServer(http.Dir("media"))).ServeHTTP(w, r)
    })

    // Routes
    http.HandleFunc("/qr", qrHandler)
    http.HandleFunc("/pair", pairHandler)
    http.HandleFunc("/send", sendHandler)
    http.HandleFunc("/send-media", sendMediaHandler)
    http.HandleFunc("/send-image-url", sendImageURLHandler)
    http.HandleFunc("/send-template", sendTemplateHandler)
    http.HandleFunc("/send-jid", sendJIDHandler)
    http.HandleFunc("/bulk", bulkHandler)
    http.HandleFunc("/contacts", contactsHandler)
    http.HandleFunc("/groups", groupsHandler)
    http.HandleFunc("/send-group", sendGroupHandler)
    http.HandleFunc("/check", checkHandler)
    http.HandleFunc("/status", statusHandler)
    http.HandleFunc("/user", userHandler)
    http.HandleFunc("/messages", messagesHandler)
    http.HandleFunc("/events", eventsHandler)
    http.HandleFunc("/logout", logoutHandler)

    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }
    addr := "0.0.0.0:" + port
    fmt.Println("WhatsApp Backend started on", addr)
    if err := http.ListenAndServe(addr, nil); err != nil {
        fmt.Println("Server error:", err)
    }
}

func resolveNumberToJID(number string) (types.JID, error) {
    num := strings.TrimPrefix(normalizeNumber(number), "+")
    if len(num) < 7 {
        return types.JID{}, fmt.Errorf("invalid phone number")
    }
    // Try WhatsApp lookup for verified JID; fall back to direct construction on any failure
    results, err := client.IsOnWhatsApp(ctx, []string{num})
    if err == nil && len(results) > 0 && results[0].IsIn {
        return results[0].JID, nil
    }
    // Fallback: build JID directly. WhatsApp will reject the send if the number is truly invalid.
    return types.NewJID(num, "s.whatsapp.net"), nil
}

// -------- HANDLERS --------

func qrHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    if client.IsLoggedIn() {
        json.NewEncoder(w).Encode(map[string]string{"error": "Already logged in"})
        return
    }

    if client.IsConnected() {
        client.Disconnect()
        time.Sleep(1 * time.Second)
    }

    qrChan, err := client.GetQRChannel(ctx)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "GetQRChannel: " + err.Error()})
        return
    }

    go func() {
        if err := client.Connect(); err != nil {
            fmt.Println("Connect error:", err)
        }
    }()

    timeout := time.After(25 * time.Second)
    for {
        select {
        case evt, ok := <-qrChan:
            if !ok {
                json.NewEncoder(w).Encode(map[string]string{"error": "QR channel closed"})
                return
            }
            switch evt.Event {
            case "code":
                json.NewEncoder(w).Encode(map[string]string{"qr": evt.Code})
                return
            case "success":
                json.NewEncoder(w).Encode(map[string]string{"success": "logged in"})
                return
            case "timeout":
                json.NewEncoder(w).Encode(map[string]string{"error": "QR timed out"})
                return
            }
        case <-timeout:
            json.NewEncoder(w).Encode(map[string]string{"error": "Timeout waiting for QR"})
            return
        }
    }
}

func pairHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    raw := r.URL.Query().Get("number")
    if raw == "" {
        json.NewEncoder(w).Encode(map[string]string{"error": "number required"})
        return
    }

    number := normalizeNumber(raw)
    if len(strings.TrimPrefix(number, "+")) < 10 {
        json.NewEncoder(w).Encode(map[string]string{"error": "invalid number format"})
        return
    }

    if client.IsLoggedIn() {
        json.NewEncoder(w).Encode(map[string]string{"error": "already logged in"})
        return
    }

    if client.IsConnected() {
        client.Disconnect()
        time.Sleep(2 * time.Second)
    }

    if err := client.Connect(); err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "connect failed: " + err.Error()})
        return
    }

    time.Sleep(5 * time.Second)

    code, err := client.PairPhone(ctx, number, true, whatsmeow.PairClientChrome, "Chrome (Linux)")
    if err != nil {
        client.Disconnect()
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error(), "number_used": number})
        return
    }

    json.NewEncoder(w).Encode(map[string]string{"code": code, "number_used": number})
}

func resolveRecipient(number string) (types.JID, error) {
    if strings.Contains(number, "@") {
        // Already a JID — strip device suffix (e.g. "91xxx:1@s.whatsapp.net" → "91xxx@s.whatsapp.net")
        atIdx := strings.LastIndex(number, "@")
        user := strings.SplitN(number[:atIdx], ":", 2)[0]
        server := number[atIdx+1:]
        return types.NewJID(user, server), nil
    }
    return resolveNumberToJID(number)
}

func sendHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    var data struct {
        Number  string `json:"number"`
        Message string `json:"message"`
    }

    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "invalid JSON body"})
        return
    }

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    jid, err := resolveRecipient(data.Number)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    msg := &waE2E.Message{Conversation: &data.Message}
    _, err = client.SendMessage(ctx, jid, msg)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    json.NewEncoder(w).Encode(map[string]string{"status": "Message Sent", "to": jid.String()})
}

func sendTemplateHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    var data struct {
        Number     string `json:"number"`
        HeaderText string `json:"header_text"`
        Body       string `json:"body"`
        Footer     string `json:"footer"`
        Buttons    []struct {
            Type string `json:"type"`
            Text string `json:"text"`
            URL  string `json:"url"`
        } `json:"buttons"`
    }

    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "invalid JSON body"})
        return
    }

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    jid, err := resolveNumberToJID(data.Number)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    hydratedButtons := make([]*waE2E.HydratedTemplateButton, 0, len(data.Buttons))
    buttonIndex := uint32(0)
    for _, btn := range data.Buttons {
        btnText := strings.TrimSpace(btn.Text)
        if btnText == "" {
            continue
        }

        switch strings.ToLower(btn.Type) {
        case "quick_reply":
            hydratedButtons = append(hydratedButtons, &waE2E.HydratedTemplateButton{
                HydratedButton: &waE2E.HydratedTemplateButton_QuickReplyButton{
                    QuickReplyButton: &waE2E.HydratedTemplateButton_HydratedQuickReplyButton{
                        DisplayText: proto.String(btnText),
                        ID:          proto.String(fmt.Sprintf("qr_%d", buttonIndex)),
                    },
                },
                Index: proto.Uint32(buttonIndex),
            })
            buttonIndex++
        case "visit_site":
            if btn.URL == "" {
                continue
            }
            hydratedButtons = append(hydratedButtons, &waE2E.HydratedTemplateButton{
                HydratedButton: &waE2E.HydratedTemplateButton_UrlButton{
                    UrlButton: &waE2E.HydratedTemplateButton_HydratedURLButton{
                        DisplayText: proto.String(btnText),
                        URL:         proto.String(btn.URL),
                    },
                },
                Index: proto.Uint32(buttonIndex),
            })
            buttonIndex++
        }
    }

    hydrated := &waE2E.TemplateMessage_HydratedFourRowTemplate{
        HydratedContentText: proto.String(data.Body),
        HydratedFooterText:  proto.String(data.Footer),
        HydratedButtons:     hydratedButtons,
    }

    if data.HeaderText != "" {
        hydrated.Title = &waE2E.TemplateMessage_HydratedFourRowTemplate_HydratedTitleText{
            HydratedTitleText: data.HeaderText,
        }
    }

    msg := &waE2E.Message{
        TemplateMessage: &waE2E.TemplateMessage{
            Format: &waE2E.TemplateMessage_HydratedFourRowTemplate_{
                HydratedFourRowTemplate: hydrated,
            },
        },
    }

    _, err = client.SendMessage(ctx, jid, msg)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    json.NewEncoder(w).Encode(map[string]string{"status": "Template sent", "to": jid.String()})
}

func sendMediaHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    if err := r.ParseMultipartForm(32 << 20); err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "failed to parse form"})
        return
    }

    number := r.FormValue("number")
    caption := r.FormValue("message")
    file, header, err := r.FormFile("file")
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "no file uploaded"})
        return
    }
    defer file.Close()

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    jid, err := resolveRecipient(number)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    // Save to temp file to read easily
    tmpFile := filepath.Join(os.TempDir(), header.Filename)
    out, err := os.Create(tmpFile)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "failed to save file"})
        return
    }
    defer out.Close()
    defer os.Remove(tmpFile)

    io.Copy(out, file)
    data, _ := os.ReadFile(tmpFile)

    mimeType := header.Header.Get("Content-Type")
    var msg *waE2E.Message

    if strings.HasPrefix(mimeType, "image/") {
        uploaded, err := client.Upload(ctx, data, whatsmeow.MediaImage)
        if err != nil {
            json.NewEncoder(w).Encode(map[string]string{"error": "upload failed: " + err.Error()})
            return
        }
        msg = &waE2E.Message{
            ImageMessage: &waE2E.ImageMessage{
                Caption:       proto.String(caption),
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
        uploaded, err := client.Upload(ctx, data, whatsmeow.MediaDocument)
        if err != nil {
            json.NewEncoder(w).Encode(map[string]string{"error": "upload failed: " + err.Error()})
            return
        }
        msg = &waE2E.Message{
            DocumentMessage: &waE2E.DocumentMessage{
                Caption:       proto.String(caption),
                URL:           proto.String(uploaded.URL),
                DirectPath:    proto.String(uploaded.DirectPath),
                MediaKey:      uploaded.MediaKey,
                Mimetype:      proto.String(mimeType),
                FileEncSHA256: uploaded.FileEncSHA256,
                FileSHA256:    uploaded.FileSHA256,
                FileLength:    proto.Uint64(uint64(len(data))),
                FileName:      proto.String(header.Filename),
            },
        }
    }

    _, err = client.SendMessage(ctx, jid, msg)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    json.NewEncoder(w).Encode(map[string]string{"status": "Media sent"})
}

func sendImageURLHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    var data struct {
        Number  string `json:"number"`
        URL     string `json:"url"`
        Caption string `json:"caption"`
    }

    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "invalid JSON body"})
        return
    }

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    jid, err := resolveNumberToJID(data.Number)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    resp, err := http.Get(data.URL)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "failed to download image: " + err.Error()})
        return
    }
    defer resp.Body.Close()

    imageData, _ := io.ReadAll(resp.Body)

    uploaded, err := client.Upload(ctx, imageData, whatsmeow.MediaImage)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "upload failed: " + err.Error()})
        return
    }

    msg := &waE2E.Message{
        ImageMessage: &waE2E.ImageMessage{
            Caption:       proto.String(data.Caption),
            URL:           proto.String(uploaded.URL),
            DirectPath:    proto.String(uploaded.DirectPath),
            MediaKey:      uploaded.MediaKey,
            Mimetype:      proto.String(http.DetectContentType(imageData)),
            FileEncSHA256: uploaded.FileEncSHA256,
            FileSHA256:    uploaded.FileSHA256,
            FileLength:    proto.Uint64(uint64(len(imageData))),
        },
    }

    _, err = client.SendMessage(ctx, jid, msg)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    json.NewEncoder(w).Encode(map[string]string{"status": "Image sent"})
}

func statusHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")
    // Store.ID is nil on a fresh/logged-out device; IsLoggedIn() uses an atomic
    // bool that can lag if old client goroutines still fire events after recreation.
    // Requiring both ensures logout is reflected immediately.
    loggedIn := client.IsLoggedIn() && client.Store.ID != nil
    json.NewEncoder(w).Encode(map[string]interface{}{
        "connected": client.IsConnected(),
        "loggedIn":  loggedIn,
    })
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    if !client.IsLoggedIn() || client.Store.ID == nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "not logged in"})
        return
    }

    myJID := client.Store.ID.ToNonAD()
    pushName := client.Store.PushName
    contact, _ := client.Store.Contacts.GetContact(ctx, myJID)

    name := pushName
    if contact.FullName != "" {
        name = contact.FullName
    }

    json.NewEncoder(w).Encode(map[string]interface{}{
        "jid":   myJID.String(),
        "name":  name,
        "phone": myJID.User,
    })
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    oldClient := client

    // Disconnect old client first
    if oldClient.IsConnected() {
        oldClient.Disconnect()
        time.Sleep(500 * time.Millisecond)
    }

    // Delete the device record from the DB (clears Store.ID)
    _ = oldClient.Store.Delete(ctx)

    // Reinitialise container to clear any in-memory cache
    newContainer, err := sqlstore.New(ctx, "sqlite", "file:store.db?_pragma=foreign_keys(1)&_pragma=journal_mode(WAL)&_pragma=busy_timeout(5000)", dbLog_)
    if err == nil {
        dbContainer = newContainer
    }

    // NewDevice() creates a guaranteed blank device (ID = nil)
    freshDevice := dbContainer.NewDevice()
    client = whatsmeow.NewClient(freshDevice, clientLog_)
    client.AddEventHandler(eventHandler)

    json.NewEncoder(w).Encode(map[string]string{"status": "logged out"})
}

func contactsHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    contacts, err := client.Store.Contacts.GetAllContacts(ctx)
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

    json.NewEncoder(w).Encode(map[string]interface{}{"contacts": list})
}

func groupsHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    groups, err := client.GetJoinedGroups(ctx)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    list := []map[string]string{}
    for _, group := range groups {
        list = append(list, map[string]string{
            "jid":  group.JID.String(),
            "name": group.Name,
        })
    }

    json.NewEncoder(w).Encode(map[string]interface{}{"groups": list})
}

func sendGroupHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    var data struct {
        GroupJID string `json:"group_jid"`
        Message  string `json:"message"`
    }

    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "invalid JSON"})
        return
    }

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    groupJID, err := parseJID(data.GroupJID)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "invalid group JID"})
        return
    }

    msg := &waE2E.Message{Conversation: &data.Message}
    _, err = client.SendMessage(ctx, groupJID, msg)
    if err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
        return
    }

    json.NewEncoder(w).Encode(map[string]string{"status": "sent"})
}

func bulkHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")

    var data struct {
        Contacts []struct {
            Name   string `json:"name"`
            Number string `json:"number"`
        } `json:"contacts"`
        Message string `json:"message"`
    }

    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        json.NewEncoder(w).Encode(map[string]string{"error": "invalid JSON"})
        return
    }

    if !client.IsConnected() {
        json.NewEncoder(w).Encode(map[string]string{"error": "not connected"})
        return
    }

    results := []map[string]interface{}{}
    for _, contact := range data.Contacts {
        jid, err := resolveNumberToJID(contact.Number)
        if err != nil {
            results = append(results, map[string]interface{}{"name": contact.Name, "number": contact.Number, "status": "failed", "error": err.Error()})
            continue
        }

        msg := &waE2E.Message{Conversation: &data.Message}
        _, err = client.SendMessage(ctx, jid, msg)
        if err != nil {
            results = append(results, map[string]interface{}{"name": contact.Name, "number": contact.Number, "status": "failed", "error": err.Error()})
        } else {
            results = append(results, map[string]interface{}{"name": contact.Name, "number": contact.Number, "status": "sent"})
        }
        time.Sleep(1 * time.Second)
    }

    json.NewEncoder(w).Encode(map[string]interface{}{"results": results})
}

// Stubs for unused handlers to prevent 404s in proxy
func sendJIDHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"error": "use /send or /send-group"})
}

func checkHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func messagesHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    w.Header().Set("Content-Type", "application/json")
    msgMu.Lock()
    defer msgMu.Unlock()
    json.NewEncoder(w).Encode(map[string]interface{}{"messages": incomingMessages})
}

func eventsHandler(w http.ResponseWriter, r *http.Request) {
    enableCORS(&w)
    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "Streaming not supported", http.StatusInternalServerError)
        return
    }
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")
    w.Header().Set("X-Accel-Buffering", "no")

    ch := make(chan []byte, 20)
    sseMu.Lock()
    sseClients[ch] = true
    sseMu.Unlock()
    defer func() {
        sseMu.Lock()
        delete(sseClients, ch)
        sseMu.Unlock()
        close(ch)
    }()

    // Send initial ping so the client knows SSE is alive
    fmt.Fprintf(w, ": connected\n\n")
    flusher.Flush()

    ticker := time.NewTicker(25 * time.Second)
    defer ticker.Stop()
    ctx := r.Context()
    for {
        select {
        case data := <-ch:
            fmt.Fprintf(w, "data: %s\n\n", data)
            flusher.Flush()
        case <-ticker.C:
            fmt.Fprintf(w, ": keepalive\n\n")
            flusher.Flush()
        case <-ctx.Done():
            return
        }
    }
}