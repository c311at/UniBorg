# (c) @UniBorg
# Original written by @UniBorg edit by @INF1N17Y

import asyncio
import logging
from collections import deque

from telethon import events

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@borg.on(events.NewMessage(pattern=r"\.clock animation", outgoing=True))
async def _(event):
    if event.fwd_from:
        return
    deq = deque(list("🕙🕘🕗🕖🕕🕔🕓🕒🕑🕐🕛"))
    for _ in range(48):
        await asyncio.sleep(0.1)
        await event.edit("".join(deq))
        deq.rotate(1)
