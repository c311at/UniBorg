# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from telethon import events
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
PRINTABLE_ASCII = range(0x21, 0x7f)


def aesthetify(string):
    for c in string:
        c = ord(c)
        if c in PRINTABLE_ASCII:
            c += 0xFF00 - 0x20
        elif c == ord(" "):
            c = 0x3000
        yield chr(c)


@borg.on(events.NewMessage(pattern=r'.ae\s+(.+)', outgoing=True)) # pylint:disable=E0602
@borg.on(events.MessageEdited(pattern=r'.ae\s+(.+)', outgoing=True)) # pylint:disable=E0602
async def _(event):
    text = event.pattern_match.group(1)
    text = "".join(aesthetify(text))
    await event.edit(text=text, parse_mode=None, link_preview=False)
    raise events.StopPropagation
