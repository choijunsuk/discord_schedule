from datetime import datetime
from config import kugaras_base_time, kugaras_interval, escu_kugaras_pattern
from scheduler import schedule_data
from alarms import set_alarms


def handle_kugaras_event(i):
    kugaras_time = (kugaras_base_time + i * kugaras_interval)
    event = escu_kugaras_pattern[i % len(escu_kugaras_pattern)]
    schedule_data.append({
        'datetime': kugaras_time,
        'event': f"쿠가라스[{kugaras_time.strftime('%p_%H:%M')}\\_{event}]"
    })
    set_alarms(schedule_data[-1])
