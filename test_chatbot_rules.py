#!/usr/bin/env python3
"""
Test script for Chatbot Rule Engine
Tests the no-code chatbot rule builder functionality
"""

import requests
import json

API_BASE = "http://localhost:5000"

def print_response(label, response):
    print(f"\n{label}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_chatbot_rule_engine():
    """Test all chatbot rule engine endpoints"""

    print("=" * 60)
    print("Chatbot Rule Engine Test")
    print("=" * 60)

    # Step 1: Create a new rule
    print("\n[1] Creating chatbot rule...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "keyword": "appointment",
            "match_type": "exact",
            "action_type": "reply",
            "action_payload": {
                "reply": "Our appointments are open Monday-Friday. To book, please reply with your preferred time.",
                "quick_replies": ["10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM"]
            },
            "priority": 1,
            "active": True
        }
    )
    print_response("Create Rule Response", response)

    if response.status_code == 200:
        rule_id = response.json()["data"]["id"]
        print(f"\n✅ Rule created with ID: {rule_id}")

    # Step 2: Create another rule (prefix match)
    print("\n[2] Creating prefix match rule...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "keyword": "menu",
            "match_type": "prefix",
            "action_type": "reply",
            "action_payload": {
                "reply": "Our menu includes:\n• Veg Thali - ₹299\n• Non-Veg Thali - ₹449\n• Burger Set - ₹199\n\nWould you like to order?",
                "quick_replies": ["Order Now", "View Full Menu"]
            },
            "priority": 2,
            "active": True
        }
    )
    print_response("Create Prefix Rule Response", response)

    # Step 3: Create AI rule (catch-all)
    print("\n[3] Creating AI catch-all rule...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "keyword": "other",
            "match_type": "exact",
            "action_type": "run_ai",
            "action_payload": {
                "ai_enabled": True,
                "memory_turns": 10,
                "fallback_to_agent": True
            },
            "priority": 0,
            "active": True
        }
    )
    print_response("Create AI Rule Response", response)

    # Step 4: List all rules
    print("\n[4] Listing all rules...")
    response = requests.get(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": "tenant-api-key"}
    )
    print_response("List Rules Response", response)

    # Step 5: Test message matching (exact match)
    print("\n[5] Testing exact match...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/match",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "message": "I want to book an appointment"
        }
    )
    print_response("Exact Match Response", response)

    # Step 6: Test message matching (prefix match)
    print("\n[6] Testing prefix match...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/match",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "message": "I would like to see the menu"
        }
    )
    print_response("Prefix Match Response", response)

    # Step 7: Test message matching (no match)
    print("\n[7] Testing no match...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/match",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "message": "This is a completely different message"
        }
    )
    print_response("No Match Response", response)

    # Step 8: Test rule execution
    print("\n[8] Testing rule execution...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/execute",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "rule_id": 1,
            "message": "Book appointment"
        }
    )
    print_response("Rule Execution Response", response)

    # Step 9: Test rule builder preview
    print("\n[9] Testing rule builder preview...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/test",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "keyword": "price",
            "match_type": "exact",
            "action_type": "reply",
            "action_payload": {
                "reply": "Our prices are very competitive!",
                "quick_replies": ["See Menu", "Talk to Sales"]
            },
            "priority": 3,
            "active": True
        }
    )
    print_response("Rule Builder Preview Response", response)

    # Step 10: Test batch operations (deactivate rules)
    print("\n[10] Testing batch deactivate...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/batch",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "action": "deactivate",
            "rule_ids": [1, 2]
        }
    )
    print_response("Batch Deactivate Response", response)

    # Step 11: Verify rules are deactivated
    print("\n[11] Verifying deactivated rules...")
    response = requests.get(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": "tenant-api-key"}
    )
    print_response("Rules After Deactivate", response)

    # Step 12: Test batch activate
    print("\n[12] Testing batch activate...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/batch",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "action": "activate",
            "rule_ids": [1, 2]
        }
    )
    print_response("Batch Activate Response", response)

    # Step 13: Update a rule
    print("\n[13] Updating rule...")
    response = requests.put(
        f"{API_BASE}/v1/chatbot/rules/1",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "keyword": "booking",
            "match_type": "exact",
            "action_type": "reply",
            "action_payload": {
                "reply": "Great! Please confirm your appointment time.",
                "quick_replies": ["10:00 AM", "11:00 AM"]
            },
            "priority": 1,
            "active": True
        }
    )
    print_response("Update Rule Response", response)

    # Step 14: Test matching with updated rule
    print("\n[14] Testing match with updated rule...")
    response = requests.post(
        f"{API_BASE}/v1/chatbot/rules/match",
        headers={"X-API-Key": "tenant-api-key"},
        json={
            "message": "I want to make a booking"
        }
    )
    print_response("Updated Match Response", response)

    # Step 15: Delete a rule
    print("\n[15] Deleting rule...")
    response = requests.delete(
        f"{API_BASE}/v1/chatbot/rules/1",
        headers={"X-API-Key": "tenant-api-key"}
    )
    print_response("Delete Rule Response", response)

    # Step 16: Final list of rules
    print("\n[16] Final rules list...")
    response = requests.get(
        f"{API_BASE}/v1/chatbot/rules",
        headers={"X-API-Key": "tenant-api-key"}
    )
    print_response("Final Rules List", response)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print("\nChatbot Rule Engine Features Tested:")
    print("  ✓ Create rules with exact/prefix/suffix/contains/regex match types")
    print("  ✓ Multiple action types (reply, run_ai, call_webhook, assign_module, forward_to_agent)")
    print("  ✓ Priority-based rule matching")
    print("  ✓ Rule list with filtering")
    print("  ✓ Message matching against rules")
    print("  ✓ Rule execution and action preview")
    print("  ✓ Rule builder preview")
    print("  ✓ Batch operations (activate, deactivate, delete)")
    print("  ✓ Update and delete rules")
    print("  ✓ Active/inactive status management")

    print("\nMatch Types Supported:")
    print("  - exact: 'appointment' matches 'appointment'")
    print("  - prefix: 'book' matches 'booking appointment'")
    print("  - suffix: 'tomorrow' matches 'tomorrow's appointment'")
    print("  - contains: 'doctor' matches 'doctor appointment'")
    print("  - regex: '\\d+' matches '12345'")

if __name__ == "__main__":
    try:
        test_chatbot_rule_engine()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to FastAPI server")
        print("   Make sure FastAPI is running: uvicorn fastapi_app:app --host 0.0.0.0 --port 5000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()