# COMBOT ANTI SPAM SYSTEM IS USED
# created for @uniborg (unfinished)

import logging
import os
import sys

from requests import get
from sample_config import Config
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)


@borg.on(events.ChatAction())
async def _(cas):
    chat = await cas.get_chat()
    user = await cas.get_user()
    if (chat.admin_rights or chat.creator):
        if cas.user_joined or cas.user_added:
            id = user.id
            mid = "{}".format(chat.title)
            mention = "[{}](tg://user?id={})".format(user.first_name, id)

            r = get(f'https://api.cas.chat/check?user_id={id}')
            r_dict = r.json()
            if r_dict['ok']:
                try:
                    who = "**Who**: {}".format(mention)
                    where = "**Where**: {}".format(mid)
                    await cas.client(
                        EditBannedRequest(
                            cas.chat_id,
                            id,
                            BANNED_RIGHTS
                        )
                    )
                    # await borg.edit_permissions(entity, user.id, view_messages=False)
                    await cas.client.send_message(
                        Config.SPAM_WATCH_LOG_CHANNEL,
                        f"**antispam log** \n{who}\n{where}\n**Action**: Banned",
                        link_preview=False
                    )
                except (Exception) as exc:
                    await cas.client.send_message(Config.PRIVATE_GROUP_BOT_API_ID, str(exc))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(
                        exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(exc)

    else:
        return ""
