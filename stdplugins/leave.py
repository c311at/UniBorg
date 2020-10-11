import time

from telethon.tl.functions.channels import LeaveChannelRequest

from uniborg.util import admin_cmd


@borg.on(admin_cmd(pattern="leave", outgoing=True))
async def leave(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        await e.delete()
        time.sleep(3)
        if '-' in str(e.chat_id):
            await borg(LeaveChannelRequest(e.chat_id))
        else:
            await e.edit('`This is Not A Chat`')
