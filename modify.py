from datetime import datetime, timedelta
import re
from scheduler import initialize_schedule, save_schedule, schedule_data

def modify_time(time_str, event_str):
    """
    주어진 시간(time_str)과 이벤트(event_str)를 기준으로 나티악 스케줄을 수정하고 이후의 스케줄을 재생성합니다.
    """
    try:
        # 시간 형식 검사 (예: 22:21)
        if not re.match(r'^\d{2}:\d{2}$', time_str):
            return "잘못된 시간 형식입니다. 예: /수정 22:21 나티악[로얄2회]"

        # 입력된 시간 파싱
        new_time = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {time_str}", '%Y-%m-%d %H:%M')

        # 현재 시간보다 과거라면 다음날로 변경
        if new_time < datetime.now():
            new_time += timedelta(days=1)

        period = "오전" if new_time.hour < 12 else "오후"

        # 이벤트 타입 파싱 (예: 나티악[로얄1회])
        match = re.match(r'^(.*)\[(.*)\]$', event_str)
        if not match:
            return "잘못된 이벤트 형식입니다. 예: /수정 22:21 나티악[로얄2회]"

        event_name, event_type = match.groups()

        # 수정할 이벤트 찾기
        event_found = False
        for scheduled_event in schedule_data:
            if event_name in scheduled_event['event']:
                scheduled_event['datetime'] = new_time
                scheduled_event['alert_5m'] = new_time - timedelta(minutes=5)
                scheduled_event['alert_1m'] = new_time - timedelta(minutes=1)
                scheduled_event['alert_sent'] = False

                character = scheduled_event['event'].split('[')[0]
                scheduled_event['event'] = f"{character}[{period}\\_{event_type}]"
                event_found = True

                # 나티악 이벤트 수정 후 로테이션 재생성
                if character == "나티악":
                    base_event = event_type[:-2]  # '로얄1회' -> '로얄'
                    count = int(event_type[-2])  # '로얄1회' -> 1
                    initialize_schedule(natiak_start_time=new_time, natiak_start_event=base_event, natiak_start_count=count)
                break

        if event_found:
            save_schedule()
            return f"{event_str}의 시간이 {new_time.strftime('%H:%M')}로 수정되었습니다."
        else:
            return f"{event_str}를 찾을 수 없습니다."

    except ValueError:
        return "잘못된 시간 형식입니다. 예: /수정 22:21 나티악[로얄2회]"
