"""CoinFlip for @UniBorg
Syntax: .coinflip [optional_choice]"""
import random
from uniborg.util import admin_cmd
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

@borg.on(admin_cmd(pattern="coinflip ?(.*)")) # pylint:disable=E0602
async def _(event):
    if event.fwd_from:
        return
    r = random.randint(1, 100)
    input_str = event.pattern_match.group(1)
    if input_str:
        input_str = input_str.lower()
    if r % 2 == 1:
        if input_str == "heads":
            await event.edit("The coin landed on: **Heads**. \n You were correct.")
        elif input_str == "tails":
            await event.edit("The coin landed on: **Heads**. \n You weren't correct, try again ...")
        else:
            await event.edit("The coin landed on: **Heads**.")
    elif r % 2 == 0:
        if input_str == "tails":
            await event.edit("The coin landed on: **Tails**. \n You were correct.")
        elif input_str == "heads":
            await event.edit("The coin landed on: **Tails**. \n You weren't correct, try again ...")
        else:
            await event.edit("The coin landed on: **Tails**.")
    else:
        await event.edit("¯\_(ツ)_/¯")
