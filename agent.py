# agent.py
import re

class KafkaOpsAgent:

    def __init__(self):
        pass

    def analyze(self, issue_body: str) -> dict:
        """
        Analyse le contenu de l'issue pour détecter l'intention et les paramètres.
        """
        intent = "unknown"
        confidence = 0.4
        params = {}

        # Détection de la demande de création de topic
        if "topic kafka" in issue_body.lower() or "création topic" in issue_body.lower():
            intent = "create_topic"
            confidence = 0.9

        # Extraction naïve des paramètres
        params["client"] = self.extract_field(issue_body, "client")
        params["event"] = self.extract_field(issue_body, "event")
        params["environnement"] = self.extract_field(issue_body, "environnement")
        params["version"] = self.extract_field(issue_body, "version")
        params["retention"] = self.extract_field(issue_body, "retention")
        params["partitions"] = self.extract_field(issue_body, "partitions")

        return {
            "intent": intent,
            "confidence": confidence,
            "parameters": params
        }

    def extract_field(self, text: str, field: str) -> str:
        """
        Recherche un champ type "field: value" dans le texte.
        """
        match = re.search(rf"{field}\s*:\s*(.+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None
