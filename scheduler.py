from datetime import datetime, timedelta
import json
from config import (spoon_fixed_pattern, escu_kugaras_pattern, natiak_order,
                    kugaras_interval, escu_interval, spoon_interval, natiak_interval)

# schedule_data를 전역 변수로 선언
schedule_data = []
natiak_count = {'오메가': 0, '혈맹': 0, '로얄': 0}
natiak_index = 0

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


def save_schedule():
    """스케줄 데이터를 파일에 저장"""
    # 시간 순으로 정렬하여 최신 데이터가 맨 뒤에 오도록 정렬
    sorted_schedule_data = sorted(schedule_data, key=lambda x: x['datetime'])

    with open("schedule_data.json", "w", encoding="utf-8") as f:
        json_data = []
        for event in sorted_schedule_data:
            event_copy = event.copy()
            event_copy['datetime'] = event['datetime'].strftime('%Y-%m-%d %H:%M:%S')
            event_copy['alert_5m'] = event['alert_5m'].strftime('%Y-%m-%d %H:%M:%S') if event['alert_5m'] else None
            event_copy['alert_1m'] = event['alert_1m'].strftime('%Y-%m-%d %H:%M:%S') if event['alert_1m'] else None
            json_data.append(event_copy)
        # ensure_ascii=False로 유니코드가 아닌 원래 문자열로 저장
        json.dump(json_data, f, ensure_ascii=False, indent=4)


def load_schedule():
    """파일에서 스케줄 데이터 로드"""
    global schedule_data
    try:
        with open("schedule_data.json", "r") as f:
            schedule_data = json.load(f)
            for event in schedule_data:
                event['datetime'] = datetime.strptime(event['datetime'], '%Y-%m-%d %H:%M:%S')
    except (FileNotFoundError, json.JSONDecodeError):
        # 데이터가 없으면 현재 시간을 기준으로 초기화
        schedule_data = []
        initialize_schedule()  # 현재 시간을 기준으로 스케줄 초기화



def initialize_schedule(natiak_start_time=None, natiak_start_event=None, natiak_start_count=None):
    global schedule_data, natiak_count, natiak_index

    current_time = datetime.now()  # 현재 시스템 시간을 기준으로 설정

    if natiak_start_time and natiak_start_event is not None and natiak_start_count is not None:
        # 수정된 시간 이후의 나티악 이벤트만 남기고 이전 이벤트 삭제
        schedule_data = [
            event for event in schedule_data if event['datetime'] >= natiak_start_time
        ]
        current_time = natiak_start_time
        current_event = natiak_start_event
        natiak_count[current_event] = natiak_start_count

        # 수정된 시점의 나티악 이벤트 추가
        add_to_schedule(current_time, '나티악', current_event, natiak_count[current_event])

        # 나티악 이벤트를 수정된 시점 이후부터 다시 생성
        while True:
            # 다음 이벤트 시간 계산
            current_time += natiak_interval
            natiak_count[current_event] += 1

            if natiak_count[current_event] > 3:
                natiak_count[current_event] = 1
                natiak_index = (natiak_index + 1) % len(natiak_order)
                current_event = natiak_order[natiak_index]

            add_to_schedule(current_time, '나티악', current_event, natiak_count[current_event])

            # 필요한 범위까지만 이벤트 생성 (예: 7일간의 이벤트 생성)
            if current_time > natiak_start_time + timedelta(days=7):
                break

        # 스케줄 데이터를 시간 순으로 정렬하여 저장
        schedule_data = sorted(schedule_data, key=lambda x: x['datetime'])

    else:
        # 현재 시스템 시간을 기준으로 기본 스케줄 생성
        start_time = current_time

        schedule_data = []
        natiak_count = {'오메가': 0, '혈맹': 0, '로얄': 0}
        natiak_index = 0
        for i in range(7):  # 7일 동안의 스케줄 생성
            spoon_time = (start_time + i * spoon_interval)
            escu_time = (start_time + i * escu_interval)
            kugaras_time = (start_time + i * kugaras_interval)
            natiak_time = (start_time + i * natiak_interval)

            # 스푸나: 월화수는 오메가 고정, 나머지는 기존 패턴
            add_to_schedule(spoon_time, '스푸나', spoon_fixed_pattern[i % len(spoon_fixed_pattern)])

            # 에스쿠: 로얄부터 시작하도록 패턴 적용
            escu_pattern = escu_kugaras_pattern[i % len(escu_kugaras_pattern)]
            add_to_schedule(escu_time, '에스쿠', escu_pattern)

            # 쿠가라스: 로얄부터 시작하도록 패턴 적용
            kugaras_pattern = escu_kugaras_pattern[i % len(escu_kugaras_pattern)]
            add_to_schedule(kugaras_time, '쿠가라스', kugaras_pattern)

            # 나티악: 3번 반복 후 다음으로 넘어가는 로직 추가
            current_event = natiak_order[natiak_index]
            natiak_count[current_event] += 1
            add_to_schedule(natiak_time, '나티악', current_event, natiak_count[current_event])

            if natiak_count[current_event] == 3:
                natiak_count[current_event] = 1  # 3회 완료 후 카운트 리셋
                natiak_index = (natiak_index + 1) % len(natiak_order)  # 다음 패턴으로 이동

    save_schedule()
load_schedule()
