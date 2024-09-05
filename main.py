import discord
from discord.ext import commands
from config import TOKEN, CHANNEL_ID, save_times, start_date, kugaras_base_time, escu_base_time, spoon_base_time, natiak_base_time
from messaging import schedule_messages
from modify import modify_time
from scheduler import initialize_schedule, schedule_data
from datetime import datetime, timedelta

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    bot.loop.create_task(schedule_messages(channel))
    save_times(start_date, kugaras_base_time, escu_base_time, spoon_base_time, natiak_base_time)

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

# /수정 커맨드 등록
@bot.command(name='수정')
async def modify_time_command(ctx, time: str, event: str):
    await modify_time(ctx, time, event)

# 스케줄 초기화
initialize_schedule()

# Discord 봇 실행
bot.run(TOKEN)
