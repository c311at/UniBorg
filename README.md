# uniborg

Pluggable [``asyncio``](https://docs.python.org/3/library/asyncio.html)
[Telegram](https://telegram.org) userbot based on
[Telethon](https://github.com/LonamiWebs/Telethon).


[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/muhammedfurkan/UniBorg)

#### Other way 

[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/muhammedfurkan/UniBorg)

### Performance Test || Resolved Issues || Active Issues

[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/muhammedfurkan/UniBorg/?ref=repository-badge)

[![DeepSource](https://deepsource.io/gh/muhammedfurkan/UniBorg.svg/?label=resolved+issues&show_trend=true)](https://deepsource.io/gh/muhammedfurkan/UniBorg/?ref=repository-badge)

[![DeepSource](https://deepsource.io/gh/muhammedfurkan/UniBorg.svg/?label=active+issues&show_trend=true)](https://deepsource.io/gh/muhammedfurkan/UniBorg/?ref=repository-badge)

### Code Quality

[![CodeFactor](https://www.codefactor.io/repository/github/muhammedfurkan/uniborg/badge)](https://www.codefactor.io/repository/github/muhammedfurkan/uniborg)

#### The Easy Way
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/muhammedfurkan/UniBorg)

#### The Legacy Way
Simply clone the repository and run the main file:
```sh
git clone https://github.com/muhammedfurkan/uniborg.git
cd uniborg
virtualenv -p /usr/bin/python3 venv
. ./venv/bin/activate
pip install -r requirements.txt
# <Create config.py with variables as given below>
python3 -m stdborg YourSessionName
```

An example `config.py` file could be:

**Not All of the variables are mandatory**

__The UniBorg should work by setting only these variables__

```python3
from sample_config import Config

class Development(Config):
  APP_ID = 6
  API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
  TG_BOT_TOKEN_BF_HER = ""
  TG_BOT_USER_NAME_BF_HER = ""
  UB_BLACK_LIST_CHAT = [
    -1001220993104,
    -1001365798550,
    -1001158304289,
    -1001212593743,
    -1001195845680,
    -1001330468518,
    -1001221185967,
    -1001340243678,
    -1001135438308,
    -1001038774929,
    -1001070622614,
    -1001119331451,
    -1001095401841
  ]
  # specify LOAD and NO_LOAD
  LOAD = []
  NO_LOAD = []
```

## internals

The core features offered by the custom `TelegramClient` live under the
[`uniborg/`](https://github.com/muhammedfurkan/uniborg/tree/master/uniborg)
directory, with some utilities, enhancements, the `_core` plugin, and the `_inline_bot` plugin.


## [@By_Azade](https://telegram.dog/By_Azade)

- Only two of the environment variables are mandatory.
- This is because of `telethon.errors.rpc_error_list.ApiIdPublishedFloodError`
    - `APP_ID`:   You can get this value from https://my.telegram.org
    - `API_HASH`:   You can get this value from https://my.telegram.org
- The userbot will work without setting the non-mandatory environment variables.
- Please report any issues to the support group: [support group](https://t.me/joinchat/AHAujEjG4FBO-TH-NrVVbg)


## design

The modular design of the project enhances your Telegram experience
through [plugins](https://github.com/SpEcHiDe/uniborg/tree/master/stdplugins)
which you can enable or disable on demand.

Each plugin gets the `borg`, `logger`, `Config`, `tgbot` magical
[variables](https://github.com/muhammedfurkan/UniBorg/blob/488eff632e65103ba7017d4f52777d22ddd52ea2/uniborg/uniborg.py#L76-L80)
to ease their use. Thus creating a plugin as easy as adding
a new file under the plugin directory to do the job:

```python
# stdplugins/myplugin.py
@borg.on(utils.admin_cmd(pattern="hi"))
async def handler(event):
    await event.reply("hey")
```


## learning

Check out the already-mentioned [plugins](https://github.com/SpEcHiDe/muhammedfurkan/tree/master/stdplugins) directory, or some third-party [plugins](https://telegram.dog/UniBorg) to learn how to write your own, and consider reading [Telethon's documentation](http://telethon.readthedocs.io/).


## credits


Thanks to:
- [lonami](https://lonami.dev) for creating [Telethon](https://github.com/lonamiwebs/Telethon)

