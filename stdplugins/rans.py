﻿# (c) @UniBorg
# Original written by @UniBorg edit by @INF1N17Y
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
from telethon import events
import asyncio
from collections import deque


@borg.on(events.NewMessage(pattern=r"\.kos", outgoing=True)) # pylint:disable=E0602
async def _(event):
	if event.fwd_from:
		return
	deq = deque(list("🚶🏃🚶🏃🚶🏃🚶🏃"))
	for _ in range(48):
		await asyncio.sleep(0.1)
		await event.edit("".join(deq))
		deq.rotate(1)
    
