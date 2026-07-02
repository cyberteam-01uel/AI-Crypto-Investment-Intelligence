import requests
import uuid
import json

# n8n webhook URL (test mode)
url = "http://localhost:5678/webhook-test/survey"

# test payload
payload = {
    "session_id": str(uuid.uuid4()),
    "message": "I want long-term investment in crypto but I panic when market drops",
    "step": 1,
    "previous_profile": {}
}

# send request
response = requests.post(
    url,
    json=payload,
    headers={
        "Content-Type": "application/json"
    }
)

# print raw response
print("\n=== STATUS CODE ===")
print(response.status_code)

print("\n=== RAW RESPONSE ===")
print(response.text)

# try parse JSON
try:
    data = response.json()

    print("\n=== PARSED RESPONSE ===")
    print(json.dumps(data, indent=2))

except Exception as e:
    print("\n❌ JSON parse failed:", str(e))