
from datetime import datetime
<<<<<<< HEAD

from uniborg import utils
=======
>>>>>>> parent of 42483031... import utils


@borg.on(utils.admin_cmd(pattern="ping", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    start = datetime.now()
    await event.edit("Pong!")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit("Pong!\n`{}`".format(ms))
