# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import asyncio
import logging
import math
import os
import re
import time
from typing import List

from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import GetPeerDialogsRequest
from telethon.tl.types import (ChannelParticipantAdmin,
                               ChannelParticipantCreator)

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)
# from alive_progress import alive_bar

# the secret configuration specific things
ENV = bool(os.environ.get("ENV", False))
if ENV:
    from sample_config import Config
else:
    if os.path.exists("config.py"):
        from sample_config import Development as Config


def get_arg(message):
    msg = message.raw_text
    msg = msg.replace(" ", "", 1) if msg[1] == " " else msg
    split = msg[1:].replace("\n", " \n").split(" ")
    if " ".join(split[1:]).strip() == "":
        return ""
    return " ".join(split[1:])


def arg_split_with(message, char):
    args = get_arg(message).split(char)
    for space in args:
        if space.strip() == "":
            args.remove(space)
    return args


async def reply(message, msg):
    await message.client.send_message(message.chat_id, msg, reply_to=message.id)


def admin_cmd(**args):
    pattern = args.get("pattern", None)
    allow_sudo = args.get("allow_sudo", False)

    # get the pattern from the decorator
    if pattern is not None:
        if pattern.startswith("\#"):
            # special fix for snip.py
            args["pattern"] = re.compile(pattern)
        else:
            args["pattern"] = re.compile(Config.COMMAND_HAND_LER + pattern)

    args["outgoing"] = True
    # should this command be available for other users?
    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        # Mutually exclusive with outgoing (can only set one of either).
        args["incoming"] = True
        del args["allow_sudo"]

    # error handling condition check
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    # add blacklist chats, UB should not respond in these chats
    args["blacklist_chats"] = True
    black_list_chats = list(Config.UB_BLACK_LIST_CHAT)
    if black_list_chats:
        args["chats"] = black_list_chats

    return events.NewMessage(**args)


async def is_read(borg, entity, message, is_out=None):
    """
    Returns True if the given message (or id) has been read
    if a id is given, is_out needs to be a bool
    """
    is_out = getattr(message, "out", is_out)
    if not isinstance(is_out, bool):
        raise ValueError(
            "Message was id but is_out not provided or not a bool")
    message_id = getattr(message, "id", message)
    if not isinstance(message_id, int):
        raise ValueError("Failed to extract id from message")

    dialog = (await borg(GetPeerDialogsRequest([entity]))).dialogs[0]
    max_id = dialog.read_outbox_max_id if is_out else dialog.read_inbox_max_id
    return message_id <= max_id


async def progress(current, total, event, start, type_of_ps):
    """Generic progress_callback for both
    upload.py and download.py"""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "[{0}{1}]\nPercent: {2}%\n".format(
            ''.join("█" for _ in range(math.floor(percentage / 5))),
            ''.join("░" for _ in range(20 - math.floor(percentage / 5))),
            round(percentage, 2))
        tmp = progress_str + \
            "{0} of {1}\nETA: {2}".format(
                humanbytes(current),
                humanbytes(total),
                time_formatter(estimated_total_time)
            )
        await event.edit("{}\n {}".format(
            type_of_ps,
            tmp
        ))

# async def progress(current,total,event,start,type_of_ps):
# 	"""Faster progressbar
# 	"""
# 	now = time.time()
# 	diff = now - start
# 	if round(diff % 10.00) == 0 or current == total:
#         percentage = current * 100 / total
#         speed = current / diff
#         elapsed_time = round(diff) * 1000
#         time_to_completion = round((total - current) / speed) * 1000
#         estimated_total_time = elapsed_time + time_to_completion
#         with alive_bar(100, bar='blocks') as bar:
#         	for i in range(100):
#                 await asyncio.sleep(5)
#                 progress_str = bar()
#         tmp = progress_str + \
#             "{0} of {1}\nETA: {2}".format(
#                 humanbytes(current),
#                 humanbytes(total),
#                 time_formatter(estimated_total_time)
#             )
#         await event.edit("{}\n {}".format(
#             type_of_ps,
#             tmp
#         ))

# async def progress(current,total,event,start,type_of_ps):
#     now = time.time()
#     diff = now -start
#     if round(diff % 10.00)== 0 or current == total:
#         percentage = current * 100 / total
#         speed = current / diff
#         elapsed_time = round(diff) * 1000
#         time_to_completion = round((total - current)/speed) * 1000
#         estimated_total_time = elapsed_time + time_to_completion
#         with alive_bar(100, bar='blocks') as bar:
#             for i in range(100):
#                 await asyncio.sleep(5)
#                 progress_str = bar()
#         tmp = progress_str + \
#             "{0} of {1}\nETA: {2}".format(
#                 humanbytes(current),
#                 humanbytes(total),
#                 time_formatter(estimated_total_time)
#             )
#         await event.edit("{}\n {}".format(
#             type_of_ps,
#             tmp
#         ))


def humanbytes(size):
    """Input size in bytes,
    outputs in a human readable format"""
    # https://stackoverflow.com/a/49361727/4723940
    if not size:
        return ""
    # 2 ** 10 = 1024
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {
        0: "",
        1: "Ki",
        2: "Mi",
        3: "Gi",
        4: "Ti"
    }
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def time_formatter(milliseconds: int) -> str:
    """Inputs time in milliseconds, to get beautified time,
    as string"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]


async def is_admin(client, chat_id, user_id):
    if not str(chat_id).startswith("-100"):
        return False
    req_jo = await client(GetParticipantRequest(
        channel=chat_id,
        user_id=user_id
    ))
    chat_participant = req_jo.participant
    return isinstance(
        chat_participant, (ChannelParticipantCreator, ChannelParticipantAdmin)
    )


# Not that Great but it will fix sudo reply
async def edit_or_reply(event, text):
    if event.from_id in Config.SUDO_USERS:
        await event.delete()
        reply_to = await event.get_reply_message()
        if reply_to:
            return await reply_to.reply(text)
        else:
            return await event.reply(text)
    else:
        return await event.edit(text)


async def run_command(command: List[str]) -> (str, str):
    process = await asyncio.create_subprocess_exec(
        *command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    return t_response, e_response


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    # width = "90"
    t_response, e_response = await run_command(file_genertor_command)
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        logger.info(e_response)
        logger.info(t_response)
        return None

# https://github.com/Nekmo/telegram-upload/blob/master/telegram_upload/video.py#L26


async def cult_small_video(video_file, output_directory, start_time, end_time):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(round(time.time())) + ".mp4"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-async",
        "1",
        "-strict",
        "-2",
        out_put_file_name
    ]
    t_response, e_response = await run_command(file_genertor_command)
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        logger.info(e_response)
        logger.info(t_response)
        return None
