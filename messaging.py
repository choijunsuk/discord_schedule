# messaging.py

import asyncio
from datetime import datetime
from scheduler import schedule_data, save_schedule


async def send_message(channel, message):
    await channel.send(message)

async def schedule_messages(channel):
    while True:
        now = datetime.now().replace(second=0, microsecond=0)
        to_remove = []
        for event in schedule_data:
            if event['alert_5m'] == now and not event['alert_sent']:
                await send_message(channel, f"5분 전 알림: {event['event']}")
                event['alert_sent'] = True
            elif event['alert_1m'] == now and not event['alert_sent']:
                await send_message(channel, f"1분 전 알림: {event['event']}")
                event['alert_sent'] = True
            elif event['datetime'] == now and not event['alert_sent']:
                await send_message(channel, event['event'])
                event['alert_sent'] = True
                to_remove.append(event)
            elif event['datetime'] < now:
                to_remove.append(event)

        for event in to_remove:
            schedule_data.remove(event)

        save_schedule()
        await asyncio.sleep(1)
