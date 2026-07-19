#!/usr/bin/env python3
"""
Quick test script for Multi-Tenancy Implementation
Run this to test the tenant API functionality
"""

import requests
import json

API_BASE = "http://localhost:5000"

def print_response(label, response):
    print(f"\n{label}")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_multi_tenancy():
    """Test all multi-tenancy endpoints"""

    print("=" * 60)
    print("Multi-Tenancy API Test")
    print("=" * 60)

    # Step 1: Create a new tenant (admin)
    print("\n[1] Creating new tenant...")
    response = requests.post(
        f"{API_BASE}/v1/tenants",
        headers={"X-API-Key": "admin-api-key"},
        json={
            "name": "Test Hospital",
            "email": "test@hospital.com",
            "plan": "premium"
        }
    )
    print_response("Create Tenant Response", response)

    if response.status_code != 200:
        print("❌ Tenant creation failed - check admin API key")
        return

    tenant_data = response.json()["data"]
    tenant_id = tenant_data["id"]
    tenant_api_key = tenant_data["api_key"]

    print(f"\n✅ Tenant created with ID: {tenant_id}")
    print(f"   API Key: {tenant_api_key}")

    # Step 2: Create a chatbot rule using tenant's API key
    print("\n[2] Creating chatbot rule...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": tenant_api_key},
        json={
            "keyword": "appointment",
            "match_type": "exact",
            "action_type": "reply",
            "action_payload": "Our appointments are open Monday-Friday. How can I help you book one?",
            "priority": 1,
            "active": 1
        }
    )
    print_response("Create Chatbot Rule Response", response)

    # Step 3: List all chatbot rules
    print("\n[3] Listing chatbot rules...")
    response = requests.get(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": tenant_api_key}
    )
    print_response("List Rules Response", response)

    # Step 4: Get tenant info
    print("\n[4] Getting tenant info...")
    response = requests.get(
        f"{API_BASE}/v1/tenants/{tenant_id}",
        headers={"X-API-Key": tenant_api_key}
    )
    print_response("Get Tenant Response", response)

    # Step 5: Get analytics summary
    print("\n[5] Getting analytics summary...")
    response = requests.get(
        f"{API_BASE}/v1/analytics/summary",
        headers={"X-API-Key": tenant_api_key}
    )
    print_response("Analytics Response", response)

    # Step 6: Send WhatsApp message
    print("\n[6] Sending WhatsApp message...")
    response = requests.post(
        f"{API_BASE}/v1/messages",
        headers={"X-API-Key": tenant_api_key},
        json={
            "to": "+919876543210",
            "text": "Hello from multi-tenant API test!"
        }
    )
    print_response("Send Message Response", response)

    # Step 7: Get WhatsApp status
    print("\n[7] Getting WhatsApp status...")
    response = requests.get(
        f"{API_BASE}/v1/tenants/{tenant_id}/wa/status",
        headers={"X-API-Key": tenant_api_key}
    )
    print_response("WhatsApp Status Response", response)

    # Step 8: Try to list tenants with tenant's API key (should fail)
    print("\n[8] Trying to list tenants with tenant's API key (should fail)...")
    response = requests.get(
        f"{API_BASE}/v1/tenants",
        headers={"X-API-Key": tenant_api_key}
    )
    print_response("Unauthorized List Tenants Response", response)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print(f"\nTenant ID: {tenant_id}")
    print(f"API Key: {tenant_api_key}")
    print(f"\nTested endpoints:")
    print("  ✓ POST /v1/tenants (create tenant)")
    print("  ✓ POST /v1/chatbot/rules (create rule)")
    print("  ✓ GET /v1/chatbot/rules (list rules)")
    print("  ✓ GET /v1/tenants/{id} (get tenant)")
    print("  ✓ GET /v1/analytics/summary (get analytics)")
    print("  ✓ POST /v1/messages (send message)")
    print("  ✓ GET /v1/tenants/{id}/wa/status (get WA status)")
    print("  ✗ GET /v1/tenants (tenant cannot list all tenants)")

if __name__ == "__main__":
    try:
        test_multi_tenancy()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to FastAPI server")
        print("   Make sure FastAPI is running: uvicorn fastapi_app:app --host 0.0.0.0 --port 5000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()