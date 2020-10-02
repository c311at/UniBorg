"""FFMpeg for @UniBorg
"""
import asyncio
import logging
import os
import time
from datetime import datetime

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


@borg.on(utils.admin_cmd(pattern="ffmpegtrim"))
async def ff_mpeg_trim_cmd(event):
    if event.fwd_from:
        return
    if not os.path.exists(FF_MPEG_DOWN_LOAD_MEDIA_PATH):
        if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
            os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
        if event.reply_to_msg_id:
            start = datetime.now()
            reply_message = await event.get_reply_message()
            try:
                c_time = time.time()
                downloaded_file_name = await event.client.download_media(
                    reply_message,
                    FF_MPEG_DOWN_LOAD_MEDIA_PATH,
                    progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        progress(d, t, event, c_time, "trying to download")
                    )
                )
            except Exception as e:  # pylint:disable=C0103,W0703
                await event.edit(str(e))
            else:
                end = datetime.now()
                ms = (end - start).seconds
                await event.edit("Downloaded to `{}` in {} seconds.".format(downloaded_file_name, ms))
        else:
            await event.edit("Reply to a Telegram media file")
    else:
        await event.edit(f"a media file already exists in path. Please remove the media and try again!\n`.exec rm {FF_MPEG_DOWN_LOAD_MEDIA_PATH}`")


@borg.on(admin_cmd(pattern="ffmpegtrim"))
async def ff_mpeg_trim_cmd(event):
    if event.fwd_from:
        return
    if not os.path.exists(FF_MPEG_DOWN_LOAD_MEDIA_PATH):
        await event.edit(f"a media file needs to be downloaded, and saved to the following path: `{FF_MPEG_DOWN_LOAD_MEDIA_PATH}`")
        return
    current_message_text = event.raw_text
    cmt = current_message_text.split(" ")
    logger.info(cmt)
    start = datetime.now()
    if len(cmt) == 3:
        # output should be video
        cmd, start_time, end_time = cmt
        o = await utils.cult_small_video(
            FF_MPEG_DOWN_LOAD_MEDIA_PATH,
            Config.TMP_DOWNLOAD_DIRECTORY,
            start_time,
            end_time
        )
        logger.info(o)
        try:
            c_time = time.time()
            await event.cilent.send_file(
                event.chat_id,
                o,
                caption=" ".join(cmt[1:]),
                force_document=False,
                supports_streaming=True,
                allow_cache=False,
                # reply_to=event.message.id,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    utils.progress(d, t, event, c_time, "trying to upload")
                )
            )
            os.remove(o)
        except Exception as e:
            logger.info(str(e))
    elif len(cmt) == 2:
        # output should be image
        cmd, start_time = cmt
        o = await utils.take_screen_shot(
            FF_MPEG_DOWN_LOAD_MEDIA_PATH,
            Config.TMP_DOWNLOAD_DIRECTORY,
            start_time
        )
        logger.info(o)
        try:
            c_time = time.time()
            await event.client.send_file(
                event.chat_id,
                o,
                caption=" ".join(cmt[1:]),
                force_document=True,
                # supports_streaming=True,
                allow_cache=False,
                # reply_to=event.message.id,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    utils.progress(d, t, event, c_time, "trying to upload")
                )
            )
            os.remove(o)
        except Exception as e:
            logger.info(str(e))
    else:
        await event.edit("RTFM")
        return
    end = datetime.now()
    ms = (end - start).seconds
    await event.edit(f"Completed Process in {ms} seconds")


async def bleck_megic(evt_message) -> str:
    if Config.LT_QOAN_NOE_FF_MPEG_URL is None or \
            Config.LT_QOAN_NOE_FF_MPEG_CTD is None:
        return None
    r_m_y = await evt_message.get_reply_message()
    fwd_mesg = await r_m_y.forward_to(
        Config.LT_QOAN_NOE_FF_MPEG_CTD
    )
    return Config.LT_QOAN_NOE_FF_MPEG_URL.format(
        message_id=fwd_mesg.id
    )
