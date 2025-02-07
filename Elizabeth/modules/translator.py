import json
import os

import requests
from emoji import UNICODE_EMOJI
from googletrans import Translator
from gtts import gTTS
from telegram import ChatAction
from telegram.ext import run_async

from Elizabeth import dispatcher
from Elizabeth.modules.disable import DisableAbleCommandHandler
from Elizabeth.modules.helper_funcs.alternate import send_action, typing_action


@run_async
@typing_action
def gtrans(update, context):
    msg = update.effective_message
    args = context.args
    lang = " ".join(args)
    if not lang:
        lang = "en"
    try:
        translate_text = msg.reply_to_message.text or msg.reply_to_message.caption
    except AttributeError:
        return msg.reply_text("Give me the text to translate!")

    ignore_text = UNICODE_EMOJI.keys()
    for emoji in ignore_text:
        if emoji in translate_text:
            translate_text = translate_text.replace(emoji, "")

    translator = Translator()
    try:
        translated = translator.translate(translate_text, dest=lang)
        trl = translated.src
        results = translated.text
        msg.reply_text(
            "Translated from {} to {}.\n {}".format(
                trl, lang, results))
    except BaseException:
        msg.reply_text("Error! invalid language code.")


@run_async
@send_action(ChatAction.RECORD_AUDIO)
def gtts(update, context):
    msg = update.effective_message
    reply = " ".join(context.args)
    if not reply:
        if msg.reply_to_message:
            reply = msg.reply_to_message.text
        else:
            return msg.reply_text(
                "Reply to some message or enter some text to convert it into audio format!"
            )
        for x in "\n":
            reply = reply.replace(x, "")
    try:
        tts = gTTS(reply)
        tts.save("Elizabeth.mp3")
        with open("Elizabeth.mp3", "rb") as speech:
            msg.reply_audio(speech)
    finally:
        if os.path.isfile("Elizabeth.mp3"):
            os.remove("Elizabeth.mp3")


# Open API key
API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
URL = "http://services.gingersoftware.com/Ginger/correct/json/GingerTheText"


@run_async
@typing_action
def spellcheck(update, context):
    if update.effective_message.reply_to_message:
        msg = update.effective_message.reply_to_message

        params = dict(
            lang="US",
            clientVersion="2.0",
            apiKey=API_KEY,
            text=msg.text)

        res = requests.get(URL, params=params)
        changes = json.loads(res.text).get("LightGingerTheTextResult")
        curr_string = ""
        prev_end = 0

        for change in changes:
            start = change.get("From")
            end = change.get("To") + 1
            suggestions = change.get("Suggestions")
            if suggestions:
                # should look at this list more
                sugg_str = suggestions[0].get("Text")
                curr_string += msg.text[prev_end:start] + sugg_str
                prev_end = end

        curr_string += msg.text[prev_end:]
        update.effective_message.reply_text(curr_string)
    else:
        update.effective_message.reply_text(
            "Reply to some message to get grammar corrected text!"
        )


__mod_name__ = "Translate"

dispatcher.add_handler(DisableAbleCommandHandler(
    ["tr", "tl"], gtrans, pass_args=True))
# dispatcher.add_handler(DisableAbleCommandHandler("tts", gtts, pass_args=True))
dispatcher.add_handler(DisableAbleCommandHandler("spell", spellcheck))
