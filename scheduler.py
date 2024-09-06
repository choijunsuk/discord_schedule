import logging
from datetime import datetime, timedelta
import json
import os
from config import (spoon_fixed_pattern, escu_kugaras_pattern, natiak_order,
                    kugaras_interval, escu_interval, spoon_interval, natiak_interval)

# 전역 변수 선언
schedule_data = []
local_cache = {}

def add_to_schedule(time, character, event, count=None):
    period = "오전" if time.hour < 12 else "오후"
    formatted_event = f"{character}[{period}\\_{event}{count}회]" if count is not None else f"{character}[{period}\\_{event}]"

    # 중복 이벤트를 찾으면 덮어쓰기
    for existing_event in schedule_data:
        if existing_event['datetime'] == time and existing_event['event'].startswith(f"{character}[{period}\\_{event}"):
            existing_event['event'] = formatted_event
            existing_event['count'] = count
            existing_event['alert_5m'] = time - timedelta(minutes=5)
            existing_event['alert_1m'] = time - timedelta(minutes=1)
            return

    # 중복이 아닐 경우에만 새로운 이벤트 추가
    schedule_data.append({
        'datetime': time,
        'event': formatted_event,
        'alert_5m': time - timedelta(minutes=5),
        'alert_1m': time - timedelta(minutes=1),
        'original_event': event,
        'count': count,
        'alert_sent': False
    })

    logging.debug(f"Added event: {formatted_event} at {time}")

def initialize_schedule(natiak_start_time=None, natiak_start_event=None, natiak_start_count=None):
    global schedule_data

    if natiak_start_time and natiak_start_event is not None and natiak_start_count is not None:
        schedule_data = [
            event for event in schedule_data if event['datetime'] < natiak_start_time or not event['event'].startswith('나티악')
        ]

        current_time = natiak_start_time
        current_event = natiak_start_event
        natiak_count = {'오메가': 0, '혈맹': 0, '로얄': 0}
        natiak_index = natiak_order.index(current_event)

        natiak_count[current_event] = natiak_start_count

        add_to_schedule(current_time, '나티악', current_event, natiak_count[current_event])

        while True:
            current_time += timedelta(hours=8)
            natiak_count[current_event] += 1

            if natiak_count[current_event] > 3:
                natiak_count[current_event] = 1
                natiak_index = (natiak_index + 1) % len(natiak_order)
                current_event = natiak_order[natiak_index]

            add_to_schedule(current_time, '나티악', current_event, natiak_count[current_event])

            if current_time > datetime.now() + timedelta(days=7):
                break

        schedule_data = sorted(schedule_data, key=lambda x: x['datetime'])  # 로드된 스케줄을 정렬하여 리스트에 저장
        save_schedule()

    else:
        current_time = datetime.now()
        start_time = current_time

        schedule_data = []
        natiak_count = {'오메가': 0, '혈맹': 0, '로얄': 0}
        natiak_index = 0
        for i in range(7):  # 7일 동안의 스케줄 생성
            spoon_time = (start_time + i * spoon_interval)
            escu_time = (start_time + i * escu_interval)
            kugaras_time = (start_time + i * kugaras_interval)
            natiak_time = (start_time + i * natiak_interval)

            add_to_schedule(spoon_time, '스푸나', spoon_fixed_pattern[i % len(spoon_fixed_pattern)])
            escu_pattern = escu_kugaras_pattern[i % len(escu_kugaras_pattern)]
            add_to_schedule(escu_time, '에스쿠', escu_pattern)
            kugaras_pattern = escu_kugaras_pattern[i % len(escu_kugaras_pattern)]
            add_to_schedule(kugaras_time, '쿠가라스', kugaras_pattern)

            current_event = natiak_order[natiak_index]
            natiak_count[current_event] += 1
            add_to_schedule(natiak_time, '나티악', current_event, natiak_count[current_event])

            if natiak_count[current_event] == 3:
                natiak_count[current_event] = 1
                natiak_index = (natiak_index + 1) % len(natiak_order)

        schedule_data = sorted(schedule_data, key=lambda x: x['datetime'])  # 리스트에 저장된 데이터를 정렬
        save_schedule()

def save_schedule():
    """스케줄 데이터를 파일에 저장"""
    global schedule_data
    sorted_schedule_data = sorted(schedule_data, key=lambda x: x['datetime'])
    schedule_data = sorted_schedule_data  # 정렬된 데이터를 스케줄에 반영

    tmp_file = "schedule_data.json.tmp"  # 임시 파일 생성
    with open(tmp_file, "w", encoding="utf-8") as f:
        json_data = []
        for event in sorted_schedule_data:
            event_copy = event.copy()
            event_copy['datetime'] = event['datetime'].strftime('%Y-%m-%d %H:%M:%S')
            event_copy['alert_5m'] = event['alert_5m'].strftime('%Y-%m-%d %H:%M:%S') if event['alert_5m'] else None
            event_copy['alert_1m'] = event['alert_1m'].strftime('%Y-%m-%d %H:%M:%S') if event['alert_1m'] else None
            json_data.append(event_copy)
        json.dump(json_data, f, ensure_ascii=False, indent=4)

    os.replace(tmp_file, "schedule_data.json")  # 임시 파일을 원본 파일로 교체

def load_schedule():
    """파일에서 스케줄 데이터를 로드하여 캐시 및 스케줄에 반영"""
    global schedule_data
    try:
        with open("schedule_data.json", "r", encoding="utf-8") as f:
            schedule_data = json.load(f)
            for event in schedule_data:
                event['datetime'] = datetime.strptime(event['datetime'], '%Y-%m-%d %H:%M:%S')
                event['alert_5m'] = datetime.strptime(event['alert_5m'], '%Y-%m-%d %H:%M:%S') if event['alert_5m'] else None
                event['alert_1m'] = datetime.strptime(event['alert_1m'], '%Y-%m-%d %H:%M:%S') if event['alert_1m'] else None
    except (FileNotFoundError, json.JSONDecodeError):
        schedule_data = []
        initialize_schedule()
        save_schedule()

load_schedule()
