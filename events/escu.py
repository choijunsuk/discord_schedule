from datetime import datetime
from config import escu_base_time, escu_interval, escu_kugaras_pattern
from scheduler import schedule_data
from alarms import set_alarms


def handle_escu_event(i):
    escu_time = (escu_base_time + i * escu_interval)
    event = escu_kugaras_pattern[i % len(escu_kugaras_pattern)]
    schedule_data.append({
        'datetime': escu_time,
        'event': f"에스쿠[{escu_time.strftime('%p_%H:%M')}\\_{event}]"
    })
    set_alarms(schedule_data[-1])
