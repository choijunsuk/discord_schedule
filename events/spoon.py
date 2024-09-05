from datetime import datetime
from config import spoon_base_time, spoon_interval, spoon_fixed_pattern
from scheduler import schedule_data
from alarms import set_alarms


def handle_spoon_event(i):
    spoon_time = (spoon_base_time + i * spoon_interval)
    event = spoon_fixed_pattern[i % len(spoon_fixed_pattern)]
    schedule_data.append({
        'datetime': spoon_time,
        'event': f"스푸나[{spoon_time.strftime('%p_%H:%M')}\\_{event}]"
    })
    set_alarms(schedule_data[-1])
