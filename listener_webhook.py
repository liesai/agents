import hmac
import hashlib
import os
import re
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv

# 🔄 Charge les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

def is_valid_signature(payload_body, signature_header):
    if not signature_header:
        return False

    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        return False

    mac = hmac.new(GITHUB_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def parse_issue_payload(payload):
    issue = payload.get("issue", {})
    body = issue.get("body", "")
    if "#KafkaTopicRequest" not in body:
        return None

    pattern = r"(client|environnement|event|version|retention|partitions):\s*(\S+)"
    matches = re.findall(pattern, body)
    data = {k: v for k, v in matches}
    data["ticketId"] = issue.get("number")
    data["repository"] = payload.get("repository", {}).get("full_name")
    return data if "client" in data else None

def dispatch_to_provisioner(task_data):
    print(f"[DISPATCH] Provision task: {task_data}")

@app.route("/webhook", methods=["POST"])
def github_webhook():
    signature = request.headers.get('X-Hub-Signature-256')
    raw_data = request.data

    if not is_valid_signature(raw_data, signature):
        print("[SECURITY] Signature invalide !")
        abort(403)

    payload = request.get_json()
    if payload.get("action") not in ["opened", "edited"]:
        return jsonify({"message": "Action ignorée"}), 200

    parsed = parse_issue_payload(payload)
    if parsed:
        dispatch_to_provisioner(parsed)
        return jsonify({"message": "Ticket Kafka traité"}), 200
    else:
        return jsonify({"message": "Pas un ticket Kafka"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
