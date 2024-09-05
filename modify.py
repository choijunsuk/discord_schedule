from datetime import datetime, timedelta
from scheduler import schedule_data, initialize_schedule, save_schedule


async def modify_time(ctx, time: str, event: str):
    try:
        new_time = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {time}", '%Y-%m-%d %H:%M')
        period = "오전" if new_time.hour < 12 else "오후"
        event_found = False

        for scheduled_event in schedule_data:
            if event.split('[')[0] in scheduled_event['event']:
                scheduled_event['datetime'] = new_time
                scheduled_event['alert_5m'] = new_time - timedelta(minutes=5)
                scheduled_event['alert_1m'] = new_time - timedelta(minutes=1)
                scheduled_event['alert_sent'] = False

                character = scheduled_event['event'].split('[')[0]
                event_type = event.split('[')[1].split(']')[0] if '[' in event and ']' in event else ""
                scheduled_event['event'] = f"{character}[{period}\\_{event_type}]"
                event_found = True

                if character == "나티악":
                    base_event = event_type.split('회')[0]
                    count = int(event_type[-2])
                    initialize_schedule(
                        natiak_start_time=new_time,
                        natiak_start_event=base_event,
                        natiak_start_count=count
                    )
                break

        if event_found:
            await ctx.send(f"{event}의 시간이 {new_time.strftime('%H:%M')}로 수정되었습니다.")
            save_schedule()
        else:
            await ctx.send(f"{event}를 찾을 수 없습니다.")
    except (ValueError, IndexError):
        await ctx.send("잘못된 시간 형식입니다. 예: /수정 22:21 나티악[로얄2회]")
