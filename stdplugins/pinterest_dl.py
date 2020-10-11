"this plugin created by https://t.me/By_Azade"

import asyncio
import logging
import os
import time
from urllib import request

import requests
import wget
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyquery import PyQuery as pq
from sample_config import Config
from telethon.tl.types import DocumentAttributeVideo
from uniborg.util import admin_cmd, humanbytes, progress, run_command

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)


# Function to get download url
def get_download_url(link):
    # Make request to website
    post_request = requests.post(
        'https://www.expertsphp.com/download.php', data={'url': link})

    # Get content from post request
    request_content = post_request.content
    str_request_content = str(request_content, 'utf-8')
    return pq(str_request_content)('table.table-condensed')('tbody')('td')(
        'a'
    ).attr('href')


# Function to download video
def download_video(url):
    video_to_download = request.urlopen(url).read()
    with open(Config.TMP_DOWNLOAD_DIRECTORY + 'pinterest_video.mp4', 'wb') as video_stream:
        video_stream.write(video_to_download)


@borg.on(admin_cmd(pattern="pvid ?(.*)"))
async def pinterst_vid_img(event):
    url = event.pattern_match.group(1)
    get_url = get_download_url(url)
    # j = wget.download(get_url, Config.TMP_DOWNLOAD_DIRECTORY+"video.mp4")
    j = download_video(get_url)
    thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "thumb_image.jpg"
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    metadata = extractMetadata(createParser(j))
    duration = 0
    if metadata.has("duration"):
        duration = metadata.get('duration').seconds
        width = 0
        height = 0
        thumb = None
    if os.path.exists(thumb_image_path):
        thumb = thumb_image_path
    else:
        thumb = await take_screen_shot(
            j,
            os.path.dirname(os.path.abspath(j)),
            (duration / 2)
        )
    c_time = time.time()
    await event.client.send_file(
        event.chat_id,
        j,
        thumb=thumb,
        caption="video",
        force_document=False,
        allow_cache=False,
        reply_to=event.message.id,
        attributes=[
            DocumentAttributeVideo(
                duration=duration,
                w=width,
                h=height,
                round_message=False,
                supports_streaming=True
            )
        ],
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, event, c_time, "trying to upload")
        )
    )
    await event.client.send_message(event.chat_id, f"pinterest video\n", file=j)


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
