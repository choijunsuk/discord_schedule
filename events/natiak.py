from datetime import datetime
from config import natiak_base_time, natiak_interval, natiak_order
from scheduler import schedule_data
from alarms import set_alarms


natiak_count = {'오메가': 0, '혈맹': 0, '로얄': 0}
natiak_index = 0

def handle_natiak_event(i):
    global natiak_index, natiak_count
    natiak_time = (natiak_base_time + i * natiak_interval)
    current_event = natiak_order[natiak_index]
    natiak_count[current_event] += 1
    schedule_data.append({
        'datetime': natiak_time,
        'event': f"나티악[{natiak_time.strftime('%p_%H:%M')}\\_{current_event}{natiak_count[current_event]}회]"
    })
    set_alarms(schedule_data[-1])

    if natiak_count[current_event] == 3:
        natiak_count[current_event] = 0
        natiak_index = (natiak_index + 1) % len(natiak_order)
