
from telethon import events
from telethon.errors import ChatAdminRequiredError

# from_id = []


# @borg.on(events.NewMessage())
# async def new_msg(event):
#     from_id.insert(0, event.from_id)


@borg.on(events.MessageDeleted)
async def handler(event):
    # me = await event.client.get_me()
    # me_id = me.id
    # if not (me_id == from_id[0]):
    grup = await event.client.get_entity(event.chat_id)
    group_ismi = grup.title
    try:
        if event:
            events = await event.client.get_admin_log(event.chat_id, delete=True)
            user = await event.client.get_entity(events[0].user_id)
            if user.id == borg.me.id:
                return
            else:
                if not user.bot:
                    ismi = user.first_name
                    # if user.username is not None:
                    #     k_adi = user.username
                    # medya_down = await event.client.download_media(medya)
                    silinen_msg = events[0].old.message

                    kullanici = f"[{ismi}](tg://user?id={user.id})"
                    msg = f"**{group_ismi} Grubundan Silinen Mesaj\n\n**"\
                        f"**Silen Kişi:** __{kullanici}__\n\n**Silinen Mesaj:** __{silinen_msg}__"
                    if events[0].old.media is not None:
                        medya = events[0].old.media
                        msg = f"**{group_ismi} Grubundan Silinen Medya\n\n**"\
                            f"**Silen Kişi:** __{kullanici}__\n\n"
                        await event.client.send_message(
                            entity=-1001220834298,
                            message=msg,
                            file=medya,
                            force_document=False
                        )
                    else:
                        await event.client.send_message(
                            entity=-1001220834298,
                            message=msg
                        )
    except ChatAdminRequiredError:
        return
    except TypeError:
        return
