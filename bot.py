#!/usr/bin/python3
import time
from datetime import datetime
import os
import re
import masto
import justirc

# === CONFIG ===
server = "irc.rizon.net" #""
channel = "#akaitestch" #""
nick = "botmane10000"
user = "botmane10000"
log = "log.txt"
time_s = "%Y%m%d-%H%M%S"
url = "https://fsebugoutzone.org/jpcumbot"

last_action_time = 0
ACTION_COOLDOWN = 1.0

notif_check = 0
bot = justirc.IRCConnection()

def get_time():
    return datetime.now().strftime(time_s)

def on_connect(bot):
    bot.set_nick(nick)
    bot.send_user_packet(user)
    print("Connected to server")

def on_welcome(bot):
    bot.join_channel(channel)
    print("Joined", channel)

def get_ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def read_count(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def write_count(filepath, count):
    with open(filepath, "w") as f:
        f.write(str(count))

def on_message(bot, channel, sender, message):

    global last_action_time
    now = time.time()

    if now - last_action_time >= ACTION_COOLDOWN:
        if message.strip() == "cummed":
            log_message = f"{get_time()} {sender} said: {message}\n"
            with open(log, "a") as log_it:
                log_it.write(log_message)

            count_file = "count.txt"
            count = read_count(count_file) + 1
            write_count(count_file, count)

            ordinal = get_ordinal(count)

            irc_message = f"It has been cummed. {url}" # if want counts in IRC msg, add: for the {ordinal} time.
            bot.send_message(channel, irc_message)

            mastodon_message = f"Anonymous has cummed for the {ordinal} time."
            try:
                masto.mastodon.status_post(visibility="unlisted", status=mastodon_message)
            except Exception as e:
                bot.send_message(channel, f"Error posting to Mastodon: {e}")

            last_action_time = now
    else:
        print("Cooldown in effect.")

"""
def check_mentions(bot, channel):
    global notif_check
    now = int(time.time())
    if (now - notif_check) > 30:
        notif_check = now
        new_ats = masto.mastodon.notifications(mentions_only=True)
        for a in new_ats:
            sender = "@" + a["status"]["account"]["acct"]
            msg = a["status"]["pleroma"]["content"]["text/plain"]
            msg = ": ".join([sender, msg])
            bot.send_message(channel, msg)
        masto.mastodon.notifications_clear()
"""
        
# === REGISTER CALLBACKS ===
bot.on_connect.append(on_connect)
bot.on_welcome.append(on_welcome)
bot.on_public_message.append(on_message)

# === INIT + START ===
masto.mastodon.notifications_clear()
notif_check = int(time.time())

bot.connect(server)
bot.run_loop()