#!/usr/bin/python3

# === Essential Files Before Running ===
# Note: .gitignore is used to keep secure/sensitive files private

# touch user.secret client.secret log.txt count.txt
# echo -e "username=usernamehere\npassword=passwordhere" > login

import time
from datetime import datetime
import os
import re
import masto
import justirc

# === CONFIG ===
server = "irc.sageru.org" # "irc.rizon.net" "irc.sageru.org"
channels = ["#jp", "##jp"] # "#testakai1", "#testakai2", "#testakai3" -- "#jp", "##jp"
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
    for chan in channels:
        bot.join_channel(chan)
        print("Joined", chan)

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

def logger(m):
    with open(log, "a") as log_it:
        log_it.write(f"{get_time()} {m}\n")

def on_message(bot, channel, sender, message):

    global last_action_time
    now = time.time()

    if now - last_action_time >= ACTION_COOLDOWN:
        if message.strip() == "cummed":

            count_file = "count.txt"
            count = read_count(count_file) + 1
            ordinal = get_ordinal(count)

            irc_message = f"It has been cummed. {url}" # if want counts in IRC msg, add: for the {ordinal} time.
            mastodon_message = f"Anonymous has cummed for the {ordinal} time."

            try:
                masto.mastodon.status_post(visibility="unlisted", status=mastodon_message)
                bot.send_message(channel, irc_message)
                write_count(count_file, count)

                logger(f"{sender} said: {message}")
            except Exception as e:
                error_msg = f"Error during action block: {type(e).__name__} - {e}"
                print(error_msg)
                logger(error_msg)
                
            last_action_time = now
    else:
        print("Cooldown in effect.")
        logger("Cooldown in effect.")

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