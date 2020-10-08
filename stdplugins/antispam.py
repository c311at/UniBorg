# COMBOT ANTI SPAM SYSTEM IS USED
# created for @uniborg (unfinished)

import logging
import os
import sys

from requests import get
from sample_config import Config
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest

from stdplugins.admin import BANNED_RIGHTS

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@borg.on(events.ChatAction())
async def _(cas):
    chat = await cas.get_chat()
    if (chat.admin_rights or chat.creator):
        if cas.user_joined or cas.user_added:
            user = await cas.get_user()
            id = user.id
            mid = "{}".format(chat.title)
            mention = "[{}](tg://user?id={})".format(user.first_name, user.id)

            r = get(f'https://api.cas.chat/check?user_id={id}')
            r_dict = r.json()
            if r_dict['ok']:
                try:
                    more = r_dict['result']
                    who = "**Who**: {}".format(mention)
                    where = "**Where**: {}".format(mid)
                    await cas.client(
                        EditBannedRequest(
                            cas.chat_id,
                            user.id,
                            BANNED_RIGHTS
                        )
                    )
                    # await borg.edit_permissions(entity, user.id, view_messages=False)
                    await cas.client.send_message(
                        Config.PRIVATE_GROUP_BOT_API_ID,
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
