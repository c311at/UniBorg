import asyncio
import json
import logging
import os
from asyncio import sleep
from json import loads
from json.decoder import JSONDecodeError
from sys import setrecursionlimit

import requests
from requests import get
from telethon import events
from telethon.errors import AboutTooLongError, FloodWaitError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

# import spotify_token as st
from sample_config import Config
from uniborg.util import admin_cmd

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)

SPOTIFY_CLIENT_ID = Config.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = Config.SPOTIFY_CLIENT_SECRET
PRIVATE_GROUP_BOT_API_ID = Config.PRIVATE_GROUP_BOT_API_ID
SPOTIFY_INITIAL_TOKEN = Config.SPOTIFY_INITIAL_TOKEN
SPOTIFY_INITIAL_BIO = Config.SPOTIFY_INITIAL_BIO

KEY = '🎶'
# The bios MUST include the key. The bot will go though those and check if they are beneath telegrams character limit.
BIOS = [KEY + ' Now Playing: {interpret} - {title} {progress}/{duration}',
        KEY + ' Now Playing: {interpret} - {title}',
        KEY + ' : {interpret} - {title}',
        KEY + ' Now Playing: {title}',
        KEY + ' : {title}']

# Mind that some characters (e.g. emojis) count more in telegram more characters then in python. If you receive an
# AboutTooLongError and get redirected here, you need to increase the offset. Check the special characters you either
# have put in the KEY or in one of the BIOS with an official Telegram App and see how many characters they actually
# count, then change the OFFSET below accordingly. Since the standard KEY is one emoji and I don't have more emojis
# anywhere, it is set to one (One emoji counts as two characters, so I reduce 1 from the character limit).
OFFSET = 1
# reduce the OFFSET from our actual 70 character limit
LIMIT = 70 - OFFSET

spotify_bio_status = False


@borg.on(events.NewMessage(pattern=r"\.spsetup ?(.*)", outgoing=True))
async def set_biostgraph(event):
    body = {"client_id": Config.SPOTIFY_CLIENT_ID, "client_secret": Config.SPOTIFY_CLIENT_SECRET,
            "grant_type": "authorization_code", "redirect_uri": "https://example.com/callback",
            "code": Config.SPOTIFY_INITIAL_TOKEN}
    r = requests.post("https://accounts.spotify.com/api/token", data=body)
    save = r.json()
    to_create = {'bio': "test", 'access_token': save['access_token'], 'refresh_token': save['refresh_token'],
                 'telegram_spam': False, 'spotify_spam': False}
    with open('./database.json', 'w') as outfile:
        json.dump(to_create, outfile, indent=4, sort_keys=True)
    if os.path.exists("./database.json"):
        await event.edit("database created")


@borg.on(events.NewMessage(pattern=r"\.disablespotify ?(.*)", outgoing=True))
async def set_biodgraph(setdbio):
    await borg(UpdateProfileRequest(about=Config.DEFAULT_BIO))
    await setdbio.edit("Default bio changed")


# @borg.on(events.NewMessage(pattern=r"\.enablesp ?(.*)", outgoing=True))
# async def set_biodgraph(setdbio):
    # if os.path.exists("./database.json"):
    # await borg(UpdateProfileRequest(about=Config.DEFAULT_BIO))
    # await setdbio.edit("Default bio changed")

@borg.on(admin_cmd(pattern="sp ?(.*)"))
async def spotify(event):
    global spotify_bio_status
    if spotify_bio_status:
        spotify_bio_status = False
        await event.edit("Spotify Bio Updater is disabled!")
    else:
        spotify_bio_status = True
        await spotify_bio()
        await event.edit("Current Spotify playback will update in bio")


def ms_converter(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    if str(seconds) == '0':
        seconds = '00'
    if len(str(seconds)) == 1:
        seconds = '0' + str(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    return str(minutes) + ":" + str(seconds)


class Database:
    def __init__(self):
        try:
            self.db = json.load(open("./database.json"))
        except FileNotFoundError:
            print("You need to run generate.py first, please read the Readme.")

    def save_token(self, token):
        self.db["access_token"] = token
        self.save()

    def save_refresh(self, token):
        self.db["refresh_token"] = token
        self.save()

    def save_bio(self, bio):
        self.db["bio"] = bio
        self.save()

    def save_spam(self, which, what):
        self.db[which + "_spam"] = what

    def return_token(self):
        return self.db["access_token"]

    def return_refresh(self):
        return self.db["refresh_token"]

    def return_bio(self):
        return self.db["bio"]

    def return_spam(self, which):
        return self.db[which + "_spam"]

    def save(self):
        with open('./database.json', 'w') as outfile:
            json.dump(self.db, outfile, indent=4, sort_keys=True)


database = Database()


def save_spam(which, what):
    # see below why

    # this is if False is inserted, so if spam = False, so if everything is good.
    if not what:
        # if it wasn't normal before, we proceed
        if database.return_spam(which):
            # we save that it is normal now
            database.save_spam(which, False)
            # we return True so we can test against it and if it this function returns, we can send a fitting message
            return True
    # this is if True is inserted, so if spam = True, so if something went wrong
    else:
        # if it was normal before, we proceed
        if not database.return_spam(which):
            # we save that it is not normal now
            database.save_spam(which, True)
            # we return True so we can send a message
            return True
    # if True wasn't returned before, we can return False now so our test fails and we dont send a message
    return False


async def spotify_bio():
    global spotify_bio_status
    while spotify_bio_status:
        # SPOTIFY
        skip = False
        to_insert = {}
        oauth = {
            "Authorization": "Bearer " + database.return_token()}
        r = requests.get(
            'https://api.spotify.com/v1/me/player/currently-playing', headers=oauth)
        # 200 means user plays smth
        if r.status_code == 200:
            received = r.json()
            if received["currently_playing_type"] == "track":
                to_insert["title"] = received["item"]["name"]
                to_insert["progress"] = ms_converter(received["progress_ms"])
                to_insert["interpret"] = received['item']["artists"][0]["name"]
                to_insert["duration"] = ms_converter(
                    received["item"]["duration_ms"])
                if save_spam("spotify", False):
                    stringy = "**[INFO]**\n\nEverything returned back to normal, the previous spotify issue has been " \
                              "resolved."
                    await borg.send_message(PRIVATE_GROUP_BOT_API_ID, stringy)
            else:
                if save_spam("spotify", True):
                    # currently item is not passed when the user plays a podcast
                    string = f"**[INFO]**\n\nThe playback {received['currently_playing_type']} didn't gave me any " \
                        f"additional information, so I skipped updating the bio."
                    await borg.send_message(PRIVATE_GROUP_BOT_API_ID, string)
        # 429 means flood limit, we need to wait
        elif r.status_code == 429:
            to_wait = r.headers['Retry-After']
            logger.error(f"Spotify, have to wait for {str(to_wait)}")
            await borg.send_message(PRIVATE_GROUP_BOT_API_ID, f'**[WARNING]**\n\nI caught a spotify api limit. I shall sleep for '
                                    f'{str(to_wait)} seconds until I refresh again')
            skip = True
            await asyncio.sleep(int(to_wait))
        # 204 means user plays nothing, since to_insert is false, we dont need to change anything
        elif r.status_code == 204:
            if save_spam("spotify", False):
                stringy = "**[INFO]**\n\nEverything returned back to normal, the previous spotify issue has been " \
                          "resolved."
                await borg.send_message(PRIVATE_GROUP_BOT_API_ID, stringy)
            pass
        # 401 means our access token is expired, so we need to refresh it
        elif r.status_code == 401:
            data = {"client_id": SPOTIFY_CLIENT_ID, "client_secret": SPOTIFY_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": database.return_refresh()}
            r = requests.post(
                "https://accounts.spotify.com/api/token", data=data)
            received = r.json()
            # if a new refresh is token as well, we save it here
            try:
                database.save_refresh(received["refresh_token"])
            except KeyError:
                pass
            database.save_token(received["access_token"])
            # since we didnt actually update our status yet, lets do this without the 30 seconds wait
            skip = True
        # 502 means bad gateway, its an issue on spotify site which we can do nothing about. 30 seconds wait shouldn't
        # put too much pressure on the spotify server, so we are just going to notify the user once
        elif r.status_code == 502:
            if save_spam("spotify", True):
                string = f"**[WARNING]**\n\nSpotify returned a Bad gateway, which means they have a problem on their " \
                    f"servers. The bot will continue to run but may not update the bio for a short time."
                await borg.send_message(PRIVATE_GROUP_BOT_API_ID, string)
        # 503 means service unavailable, its an issue on spotify site which we can do nothing about. 30 seconds wait
        # shouldn't put too much pressure on the spotify server, so we are just going to notify the user once
        elif r.status_code == 503:
            if save_spam("spotify", True):
                string = f"**[WARNING]**\n\nSpotify said that the service is unavailable, which means they have a " \
                         f"problem on their servers. The bot will continue to run but may not update the bio for a " \
                         f"short time."
                await borg.send_message(PRIVATE_GROUP_BOT_API_ID, string)
        # 404 is a spotify error which isn't supposed to happen (since our URL is correct). Track the issue here:
        # https://github.com/spotify/web-api/issues/1280
        elif r.status_code == 404:
            if save_spam("spotify", True):
                string = f"**[INFO]**\n\nSpotify returned a 404 error, which is a bug on their side."
                await borg.send_message(PRIVATE_GROUP_BOT_API_ID, string)
        # catch anything else
        else:
            await borg.send_message(PRIVATE_GROUP_BOT_API_ID, '**[ERROR]**\n\nOK, so something went reeeally wrong with spotify. The bot '
                                    'was stopped.\nStatus code: ' + str(r.status_code) + '\n\nText: ' + r.text)
            logger.error(
                f"Spotify, error {str(r.status_code)}, text: {r.text}")
            # stop the whole program since I dont know what happens here and this is the safest thing we can do
            spotify_bio_status = False
        # TELEGRAM
        try:
            # full needed, since we dont get a bio with the normal request
            full = await borg(GetFullUserRequest('me'))
            bio = full.about
            # to_insert means we have a successful playback
            if to_insert:
                # putting our collected information's into nice variables
                title = to_insert["title"]
                interpret = to_insert["interpret"]
                progress = to_insert["progress"]
                duration = to_insert["duration"]
                # we need this variable to see if actually one of the bios is below the character limit
                new_bio = ""
                global BIOS, LIMIT
                for bio in BIOS:
                    temp = bio.format(
                        title=title, interpret=interpret, progress=progress, duration=duration)
                    # we try to not ignore for telegrams character limit here
                    if len(temp) < LIMIT:
                        # this is short enough, so we put it in the variable and break our for loop
                        new_bio = temp
                        break
                # if we have a bio, one bio was short enough
                if new_bio:
                    # test if the user changed his bio to blank, we save it before we override
                    if not bio:
                        database.save_bio(bio)
                    # test if the user changed his bio in the meantime, if yes, we save it before we override
                    elif "🎶" not in bio:
                        database.save_bio(bio)
                    # test if the bio isn't the same, otherwise updating it would be stupid
                    if not new_bio == bio:
                        try:
                            await borg(UpdateProfileRequest(about=new_bio))
                            if save_spam("telegram", False):
                                stringy = "**[INFO]**\n\nEverything returned back to normal, the previous telegram " \
                                          "issue has been resolved."
                                await borg.send_message(PRIVATE_GROUP_BOT_API_ID, stringy)
                        # this can happen if our LIMIT check failed because telegram counts emojis twice and python
                        # doesnt. Refer to the constants file to learn more about this
                        except AboutTooLongError:
                            if save_spam("telegram", True):
                                stringy = f'**[WARNING]**\n\nThe biography I tried to insert was too long. In order ' \
                                    f'to not let that happen again in the future, please read the part about OFFSET ' \
                                    f'in the constants. Anyway, here is the bio I tried to insert:\n\n{new_bio}'
                                await borg.send_message(PRIVATE_GROUP_BOT_API_ID, stringy)
                # if we dont have a bio, everything was too long, so we tell the user that
                if not new_bio:
                    if save_spam("telegram", True):
                        to_send = f"**[INFO]**\n\nThe current track exceeded the character limit, so the bio wasn't " \
                            f"updated.\n\n Track: {title}\nInterpret: {interpret}"
                        await borg.send_message(PRIVATE_GROUP_BOT_API_ID, to_send)
            # not to_insert means no playback
            else:
                if save_spam("telegram", False):
                    stringy = "**[INFO]**\n\nEverything returned back to normal, the previous telegram issue has " \
                              "been resolved."
                    await borg.send_message(PRIVATE_GROUP_BOT_API_ID, stringy)
                old_bio = database.return_bio()
                # this means the bio is blank, so we save that as the new one
                if not bio:
                    database.save_bio(bio)
                # this means an old playback is in the bio, so we change it back to the original one
                elif "🎶" in bio:
                    await borg(UpdateProfileRequest(about=database.return_bio()))
                # this means a new original is there, lets save it
                elif not bio == old_bio:
                    database.save_bio(bio)
                # this means the original one we saved is still valid
                else:
                    pass
        except FloodWaitError as e:
            to_wait = [int(s) for s in str(e).split() if s.isdigit()]
            logger.error(f"to wait for {str(to_wait[0])}")
            await borg.send_message(PRIVATE_GROUP_BOT_API_ID, f'**[WARNING]**\n\nI caught a telegram api limit. I shall sleep '
                                    f'{str(to_wait[0])} seconds until I refresh again')
            skip = True
            await asyncio.sleep(int(to_wait[0]))
        # skip means a flood error stopped the whole program, no need to wait another 10 seconds after that
        if not skip:
            await asyncio.sleep(10)
