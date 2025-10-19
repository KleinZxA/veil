class SuricataClient:
    def __init__(self, suricata_url):
        self.suricata_url = suricata_url

    def fetch_alerts(self):
        import requests
        try:
            response = requests.get(f"{self.suricata_url}/alerts")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching alerts: {e}")
            return []

    def fetch_logs(self):
        import requests
        try:
            response = requests.get(f"{self.suricata_url}/logs")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching logs: {e}")
            return []