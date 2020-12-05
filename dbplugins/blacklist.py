# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Filters
Available Commands:
.addblacklist
.listblacklist
.rmblacklist"""
import asyncio
import io
import re

from telethon import events
from telethon.tl import functions, types

from database.blacklistdb import (add_to_blacklist, get_chat_blacklist,
                                  rm_from_blacklist)
from sample_config import Config
from uniborg.util import admin_cmd, is_admin


@borg.on(admin_cmd(incoming=True))
async def on_new_message(event):
    if await is_admin(event.client, event.chat_id, event.sender_id):
        return
    if borg.me.id == event.sender_id:
        return
    name = event.raw_text
    snips = get_chat_blacklist(event.chat_id)
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await event.delete()
            except Exception as e:
                await event.reply("I do not have DELETE permission in this chat")
                rm_from_blacklist(event.chat_id, snip.lower())
            break


@borg.on(admin_cmd(pattern="addblacklist ((.|\n)*)"))
async def on_add_black_list(event):
    text = event.pattern_match.group(1)
    to_blacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )
    for trigger in to_blacklist:
        add_to_blacklist(event.chat_id, trigger.lower())
    await event.edit(
        "Added {} triggers to the blacklist in the current chat".format(
            len(to_blacklist)
        )
    )


@borg.on(admin_cmd(pattern="listblacklist"))
async def on_view_blacklist(event):
    all_blacklisted = get_chat_blacklist(event.chat_id)
    OUT_STR = "Blacklists in the Current Chat:\n"
    if len(all_blacklisted) > 0:
        for trigger in all_blacklisted:
            OUT_STR += f"👉 {trigger} \n"
    else:
        OUT_STR = "No BlackLists. Start Saving using `.addblacklist`"
    if len(OUT_STR) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "blacklist.text"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="BlackLists in the Current Chat",
                reply_to=event,
            )
            await event.delete()
    else:
        await event.edit(OUT_STR)


@borg.on(admin_cmd(pattern="rmblacklist ((.|\n)*)"))
async def on_delete_blacklist(event):
    text = event.pattern_match.group(1)
    to_unblacklist = list(
        {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
    )
    successful = sum(
        1
        for trigger in to_unblacklist
        if rm_from_blacklist(event.chat_id, trigger.lower())
    )

    await event.edit(f"Removed {successful} / {len(to_unblacklist)} from the blacklist")
