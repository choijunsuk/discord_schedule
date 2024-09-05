from datetime import timedelta

def set_alarms(event):
    """이벤트에 알람 시간을 설정"""
    event['alert_5m'] = event['datetime'] - timedelta(minutes=5)
    event['alert_1m'] = event['datetime'] - timedelta(minutes=1)
    event['alert_sent'] = False
