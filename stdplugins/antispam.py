# COMBOT ANTI SPAM SYSTEM IS USED
# created for @uniborg (unfinished)

import logging
import os
import sys
from uniborg import utils
from telethon import events
from sample_config import Config

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
            from requests import get
            # async with aiohttp.get()
            r = get(f'https://combot.org/api/cas/check?user_id={id}')
            # r = await aiohttp.get(f'https://combot.org/api/cas/check?user_id={id}')
            r_dict = r.json()
            if r_dict['ok']:
                try:
                    more = r_dict['result']
                    # rights = ChatBannedRights(
                    #     until_date=None,
                    #     view_messages=True,
                    #     send_messages=True
                    # )
                    # await borg.send_message('me',entity)
                    # get_entity = await event.get_participants(chat)
                    # await borg.send_message('me',get_entity)
                    # await borg(EditBannedRequest(cas.chat_id, id, rights))
                    who = "**Who**: {}".format(mention)
                    where = "**Where**: {}".format(mid)
                    how = "**How**: [here](https://combot.org/api/cas/check?user_id={})".format(
                        id)
                    # moree = "**More**: ```{}```".format(more)
                    # entity = await borg.get_entity(chat)
                    async for g in borg.iter_participants(chat):
                        entity = g.id
                    await borg.edit_permissions(entity, user.id, view_messages=False)
                    await borg.send_message(Config.PRIVATE_GROUP_BOT_API_ID, f"**antispam log** \n{who}\n{where}\n{how}\n**Action**: Banned", link_preview=False)
                except (Exception) as exc:
                    await borg.send_message(Config.PRIVATE_GROUP_BOT_API_ID, str(exc))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(
                        exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    print(exc)

    else:
        return ""
