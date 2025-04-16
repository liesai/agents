import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CONFLUENT_API_KEY = os.getenv("CONFLUENT_API_KEY")
CONFLUENT_API_SECRET = os.getenv("CONFLUENT_API_SECRET")
CLUSTER_ID = os.getenv("CONFLUENT_CLUSTER_ID")

def create_topic(topic_name, partitions, retention_ms):
    url = f"https://api.confluent.cloud/kafka/v3/clusters/{CLUSTER_ID}/topics"
    auth = (CONFLUENT_API_KEY, CONFLUENT_API_SECRET)

    payload = {
        "topic_name": topic_name,
        "partitions_count": partitions,
        "configs": [
            {
                "name": "retention.ms",
                "value": str(retention_ms)
            }
        ]
    }

    response = requests.post(url, json=payload, auth=auth)
    return response

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    issue = data.get("issue", {})
    body = issue.get("body", "")
    labels = [label["name"] for label in issue.get("labels", [])]

    if "kafka" not in labels:
        return jsonify({"message": "No kafka label found"}), 200

    def extract(field):
        for line in body.splitlines():
            if line.lower().startswith(f"{field.lower()}:"):
                return line.split(":", 1)[1].strip()
        return None

    client = extract("client")
    event = extract("event")
    env = extract("environnement")
    version = extract("version")
    retention = extract("retention")
    partitions = extract("partitions")

    if not all([client, event, env, version, retention, partitions]):
        return jsonify({"error": "Missing fields"}), 400

    topic_name = f"{client}.{event}.{version}.{env}"
    retention_ms = int(retention.replace("d", "")) * 24 * 60 * 60 * 1000
    partitions = int(partitions)

    response = create_topic(topic_name, partitions, retention_ms)

    if response.status_code == 201:
        return jsonify({"message": f"Topic {topic_name} created"}), 201
    else:
        return jsonify({
            "error": "Failed to create topic",
            "details": response.text
        }), response.status_code


