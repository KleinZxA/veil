def parse_suricata_output(data):
    parsed_data = []
    for alert in data.get('alerts', []):
        parsed_alert = {
            'timestamp': alert.get('timestamp'),
            'alert_type': alert.get('alert', {}).get('category'),
            'signature': alert.get('alert', {}).get('signature'),
            'source_ip': alert.get('src_ip'),
            'destination_ip': alert.get('dest_ip'),
            'source_port': alert.get('src_port'),
            'destination_port': alert.get('dest_port'),
        }
        parsed_data.append(parsed_alert)
    return parsed_data

def parse_suricata_logs(data):
    parsed_logs = []
    for log in data.get('logs', []):
        parsed_log = {
            'timestamp': log.get('timestamp'),
            'message': log.get('message'),
            'level': log.get('level'),
        }
        parsed_logs.append(parsed_log)
    return parsed_logs