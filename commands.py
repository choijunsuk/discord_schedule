from discord.ext import commands
from schedule import ScheduleManager

schedule_manager = ScheduleManager()

@commands.command(name='막타')
async def last_hit(ctx):
    info = schedule_manager.get_today_schedule()
    await ctx.send(info)

@commands.command(name='시간표')
async def timetable(ctx, days: int = 1):
    info = schedule_manager.get_schedule_for_days(days)
    await ctx.send(info)

@commands.command(name='수정')
async def modify_time(ctx, time: str, event: str):
    response = schedule_manager.modify_event_time(time, event)
    await ctx.send(response)
