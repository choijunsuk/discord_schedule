import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

TOKEN = 'MTI3NzkxMzkxNDQ5OTI3MjczNQ.GOMieA.bHUw64unmlWiIXjs8iE3Eh_8jLv6jbxk_dYthU'
CHANNEL_ID = 1236559949530791936  # 메시지를 보낼 채널의 ID

# Intents 설정 (기본 설정에 필요한 이벤트만 활성화)
intents = discord.Intents.default()
intents.message_content = True  # 메시지 콘텐츠 접근 허용

bot = commands.Bot(command_prefix='/', intents=intents)

# 기준 시간 설정 및 주기 설정
start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
kugaras_base_time = datetime.combine(start_date, datetime.strptime("22:42:01", "%H:%M:%S").time())
escu_base_time = datetime.combine(start_date, datetime.strptime("23:54:00", "%H:%M:%S").time())
spoon_base_time = datetime.combine(start_date, datetime.strptime("01:03:31", "%H:%M:%S").time())
natiak_base_time = datetime.combine(start_date, datetime.strptime("17:26:57", "%H:%M:%S").time())

kugaras_interval = timedelta(hours=12)
escu_interval = timedelta(hours=16)
spoon_interval = timedelta(hours=16)
natiak_interval = timedelta(hours=8)

# 스푸나 패턴 수정: 월화수는 오메가 고정
spoon_fixed_pattern = ['오메가', '오메가', '오메가', '혈맹', '로얄', '혈맹', '로얄']

# 에스쿠와 쿠가라스 패턴 수정: 로얄부터 시작
escu_kugaras_pattern = ['로얄', '혈맹']  # 로얄부터 시작하도록 변경

# 나티악 이벤트 횟수 저장용
natiak_count = {'오메가': 0, '혈맹': 0, '로얄': 0}
natiak_order = ['오메가', '혈맹', '로얄']  # 나티악 패턴 순서
natiak_index = 0  # 현재 나티악 패턴 인덱스

# 스케줄 데이터 생성
schedule_data = []

def add_to_schedule(time, character, event, count=None):
    period = "오전" if time.hour < 12 else "오후"
    if character == "나티악" and count is not None:
        formatted_event = f"{character}[{period}\\_{event}{count}회]"  # 나티악 이벤트는 횟수 포함
    else:
        formatted_event = f"{character}[{period}\\_{event}]"  # 나머지 이벤트는 횟수 미포함
    schedule_data.append({
        'datetime': time,
        'event': formatted_event,
        'alert_5m': time - timedelta(minutes=5),
        'alert_1m': time - timedelta(minutes=1),
        'original_event': event,  # 원래 이벤트 저장
        'count': count,
        'alert_sent': False  # 알림이 보내졌는지 여부
    })

# 스케줄 초기화 및 생성
def initialize_schedule(natiak_start_time=None, natiak_start_event=None, natiak_start_count=None):
    global schedule_data
    global natiak_count
    global natiak_index

    if natiak_start_time and natiak_start_event is not None and natiak_start_count is not None:
        # 기존 나티악 이벤트 삭제 및 재배치
        schedule_data = [
            event for event in schedule_data
            if not event['event'].startswith('나티악') or event['datetime'] < natiak_start_time
        ]
        current_time = natiak_start_time
        current_event = natiak_start_event
        natiak_count[current_event] = natiak_start_count

        # 나티악 이벤트를 수정된 시점부터 다시 생성
        for i in range(natiak_start_count, 4):
            add_to_schedule(current_time, '나티악', current_event, i)
            current_time += natiak_interval

        natiak_index = (natiak_order.index(current_event) + 1) % len(natiak_order)

        # 나티악 이후의 이벤트 생성
        current_event = natiak_order[natiak_index]
        for i in range(1, 4):
            add_to_schedule(current_time, '나티악', current_event, i)
            current_time += natiak_interval

    else:
        # 기존 방식으로 스케줄 생성
        schedule_data = []
        natiak_count = {'오메가': 0, '혈맹': 0, '로얄': 0}
        natiak_index = 0
        for i in range(7):
            spoon_time = (spoon_base_time + i * spoon_interval)
            escu_time = (escu_base_time + i * escu_interval)
            kugaras_time = (kugaras_base_time + i * kugaras_interval)
            natiak_time = (natiak_base_time + i * natiak_interval)

            # 스푸나: 월화수는 오메가 고정, 나머지는 기존 패턴
            add_to_schedule(spoon_time, '스푸나', spoon_fixed_pattern[i])

            # 에스쿠: 로얄부터 시작하도록 패턴 적용
            escu_pattern = escu_kugaras_pattern[i % 2]
            add_to_schedule(escu_time, '에스쿠', escu_pattern)

            # 쿠가라스: 로얄부터 시작하도록 패턴 적용
            kugaras_pattern = escu_kugaras_pattern[i % 2]
            add_to_schedule(kugaras_time, '쿠가라스', kugaras_pattern)

            # 나티악: 3번 반복 후 다음으로 넘어가는 로직 추가
            current_event = natiak_order[natiak_index]
            natiak_count[current_event] += 1
            add_to_schedule(natiak_time, '나티악', current_event, natiak_count[current_event])

            if natiak_count[current_event] == 3:
                natiak_count[current_event] = 0  # 3회 완료 후 카운트 리셋
                natiak_index = (natiak_index + 1) % len(natiak_order)  # 다음 패턴으로 이동

# 스케줄 초기화
initialize_schedule()

async def send_message(channel, message):
    await channel.send(message)

async def schedule_messages():
    while True:
        now = datetime.now().replace(second=0, microsecond=0)
        to_remove = []
        for event in schedule_data:
            if event['alert_5m'] == now and not event['alert_sent']:
                await send_message(channel, f"5분 전 알림: {event['event']}")
                event['alert_sent'] = True  # 알림이 한 번만 울리도록 설정
            elif event['alert_1m'] == now and not event['alert_sent']:
                await send_message(channel, f"1분 전 알림: {event['event']}")
                event['alert_sent'] = True  # 알림이 한 번만 울리도록 설정
            elif event['datetime'] == now and not event['alert_sent']:
                await send_message(channel, event['event'])
                event['alert_sent'] = True  # 알림이 한 번만 울리도록 설정
                to_remove.append(event)
            elif event['datetime'] < now:
                to_remove.append(event)  # 이미 지난 이벤트는 제거

        # 시간이 지난 이벤트 삭제
        for event in to_remove:
            schedule_data.remove(event)

        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    global channel
    channel = bot.get_channel(CHANNEL_ID)
    bot.loop.create_task(schedule_messages())
# /막타 커맨드 정의: 하루 스케줄 표시
@bot.command(name='막타')
async def last_hit(ctx):
    today = datetime.now().date()
    info = "오늘의 스케줄:\n"
    todays_events = sorted(
        [event for event in schedule_data if event['datetime'].date() == today],
        key=lambda x: x['datetime']
    )
    if not todays_events:
        info += "오늘 스케줄이 없습니다."
    for event in todays_events:
        info += f"{event['datetime'].strftime('%Y-%m-%d')}: {event['event']}\n"
    await ctx.send(info)

# /시간표 커맨드 정의: 사용자가 입력한 일 수만큼의 스케줄 표시
@bot.command(name='시간표')
async def timetable(ctx, days: int = 1):  # 기본값은 하루(1일)로 설정
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    info = f"{days}일간의 스케줄:\n"
    multi_day_events = sorted(
        [event for event in schedule_data if today <= event['datetime'].date() < end_date],
        key=lambda x: x['datetime']
    )
    if not multi_day_events:
        info += "해당 기간에 스케줄이 없습니다."
    for event in multi_day_events:
        info += f"{event['datetime'].strftime('%Y-%m-%d %H:%M')}: {event['event']}\n"
    await ctx.send(info)

# /수정 커맨드 정의: 특정 이벤트의 시간을 수정
@bot.command(name='수정')
async def modify_time(ctx, time: str, event: str):
    try:
        # 입력받은 시간과 이벤트 이름을 처리
        new_time = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {time}", '%Y-%m-%d %H:%M')
        period = "오전" if new_time.hour < 12 else "오후"
        event_found = False

        for scheduled_event in schedule_data:
            if event.split('[')[0] in scheduled_event['event']:
                # 이벤트 시간과 이름 수정
                scheduled_event['datetime'] = new_time
                scheduled_event['alert_5m'] = new_time - timedelta(minutes=5)
                scheduled_event['alert_1m'] = new_time - timedelta(minutes=1)
                scheduled_event['alert_sent'] = False  # 수정된 이벤트에 대해 알림이 다시 설정되도록 초기화

                # 이벤트 형식을 새로 고침
                character = scheduled_event['event'].split('[')[0]
                if '[' in event and ']' in event:
                    event_type = event.split('[')[1].split(']')[0]
                else:
                    raise ValueError("이벤트 형식이 잘못되었습니다.")

                # 이벤트를 올바르게 업데이트
                scheduled_event['event'] = f"{character}[{period}\\_{event_type}]"
                event_found = True

                # 나티악 이벤트일 경우 이후 스케줄 재조정
                if character == "나티악":
                    base_event = event_type.split('회')[0]  # '로얄'을 추출
                    count = int(event_type[-2])  # '2회'의 숫자 '2'를 추출
                    initialize_schedule(
                        natiak_start_time=new_time,
                        natiak_start_event=base_event,
                        natiak_start_count=count
                    )
                break

        if event_found:
            await ctx.send(f"{event}의 시간이 {new_time.strftime('%H:%M')}로 수정되었습니다.")
        else:
            await ctx.send(f"{event}를 찾을 수 없습니다.")

    except (ValueError, IndexError):
        await ctx.send("잘못된 시간 형식입니다. 예: /수정 22:21 나티악[로얄2회]")

bot.run(TOKEN)
