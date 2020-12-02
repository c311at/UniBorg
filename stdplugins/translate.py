""" Google Translate
Available Commands:
.tr LanguageCode as reply to a message
.tr LangaugeCode | text to translate"""
from googletrans import LANGUAGES, Translator

from uniborg.util import admin_cmd


@borg.on(admin_cmd(pattern="tr ?(.*)"))
async def _(event):
    if event.fwd_from:
        return
    if "trim" in event.raw_text:
        # https://t.me/c/1220993104/192075
        return
    input_str = event.pattern_match.group(1)
    if event.reply_to:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "en"
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.edit("`.tr LanguageCode` as reply to a message")
        return
    text = text.strip()
    lan = lan.strip()
    translator = Translator(service_urls=["translate.googleapis.com"])
    try:
        translated = translator.translate(text, dest=lan)
        after_tr_text = translated.text
        source_lan = LANGUAGES[f"{translated.src.lower()}"]
        transl_lan = LANGUAGES[f"{translated.dest.lower()}"]
        output_str = "Detected Language: **{}**\nTRANSLATED To: **{}**\n\n{}".format(
            # previous_message.message,
            source_lan.title(),
            transl_lan.title(),
            after_tr_text,
        )
        await event.edit(output_str)
    except Exception as exc:
        await event.edit(str(exc))
