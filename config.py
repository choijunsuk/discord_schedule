import os
from datetime import datetime, timedelta
import json

# Discord 설정
TOKEN = 'MTI3NzkxMzkxNDQ5OTI3MjczNQ.GOMieA.bHUw64unmlWiIXjs8iE3Eh_8jLv6jbxk_dYthU'
CHANNEL_ID = 1236559949530791936  # 메시지를 보낼 채널의 ID

# 시간 관련 설정 파일
TIME_FILE = "default_times.json"

def load_times():
    """저장된 시간을 불러오거나 현재 시간을 반환"""
    current_time = datetime.now().replace(second=0, microsecond=0)
    try:
        with open(TIME_FILE, "r") as f:
            times = json.load(f)
            start_date = datetime.strptime(times['start_date'], '%Y-%m-%d %H:%M:%S')
            kugaras_base_time = datetime.strptime(times['kugaras_base_time'], '%Y-%m-%d %H:%M:%S')
            escu_base_time = datetime.strptime(times['escu_base_time'], '%Y-%m-%d %H:%M:%S')
            spoon_base_time = datetime.strptime(times['spoon_base_time'], '%Y-%m-%d %H:%M:%S')
            natiak_base_time = datetime.strptime(times['natiak_base_time'], '%Y-%m-%d %H:%M:%S')

            # 만약 00:00분인 경우 현재 시간으로 대체
            if start_date.time() == datetime.min.time():
                start_date = current_time
            if kugaras_base_time.time() == datetime.min.time():
                kugaras_base_time = current_time
            if escu_base_time.time() == datetime.min.time():
                escu_base_time = current_time
            if spoon_base_time.time() == datetime.min.time():
                spoon_base_time = current_time
            if natiak_base_time.time() == datetime.min.time():
                natiak_base_time = current_time

            return start_date, kugaras_base_time, escu_base_time, spoon_base_time, natiak_base_time
    except (FileNotFoundError, ValueError):
        return (current_time, current_time, current_time, current_time, current_time)

def save_times(start_date, kugaras_base_time, escu_base_time, spoon_base_time, natiak_base_time):
    """현재 시간을 파일에 저장"""
    times = {
        'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
        'kugaras_base_time': kugaras_base_time.strftime('%Y-%m-%d %H:%M:%S'),
        'escu_base_time': escu_base_time.strftime('%Y-%m-%d %H:%M:%S'),
        'spoon_base_time': spoon_base_time.strftime('%Y-%m-%d %H:%M:%S'),
        'natiak_base_time': natiak_base_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(TIME_FILE, "w") as f:
        json.dump(times, f)

# 스푸나 패턴 설정: 월, 화, 수는 오메가 고정, 목요일부터 혈맹, 로얄 패턴
spoon_fixed_pattern = ['오메가', '오메가', '오메가', '혈맹', '로얄', '혈맹', '로얄']

# 에스쿠와 쿠가라스 패턴: 로얄부터 시작
escu_kugaras_pattern = ['로얄', '혈맹']

# 나티악 패턴 순서
natiak_order = ['혈맹', '오메가', '로얄']

# 기본 시간을 불러오거나 현재 시간을 설정
start_date, kugaras_base_time, escu_base_time, spoon_base_time, natiak_base_time = load_times()

kugaras_interval = timedelta(hours=12)
escu_interval = timedelta(hours=16)
spoon_interval = timedelta(hours=16)
natiak_interval = timedelta(hours=8)
