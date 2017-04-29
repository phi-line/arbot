import os
from os.path import isfile, join, dirname, abspath
from datetime import datetime
from urllib.parse import urlencode

import discord
from discord.ext import commands
from discord.ext.commands import Bot
import secrets

from pokemon import pkmn

client = discord.Client()
pibot = Bot(command_prefix="!")
# pibot = commands.Bot(command_prefix='!')
bot_name = 'snek-bot'

@pibot.async_event
async def on_ready():
    print("Logged in as {}".format(bot_name))

@pibot.command(pass_context=True)
async def ls(ctx, *, args):
    print(args)
    print(len(args))
    if args == "help":
        return await pibot.send_message(ctx.message.author,
                                        "Command list: !tw !yt !dd !py !dpy !ti !pyg"
                                        "\n\nType !ls \"command\" for help on that topic.")
    elif args == "tw":
        return await pibot.send_message(ctx.message.author,
                                        "This command is used to link a twitch user's stream."
                                        "\n\n<syntax> !tw \"username\"")
    elif args == "yt":
        return await pibot.send_message(ctx.message.author,
                                        "This command is used to link youtube searches."
                                        "\n\n<syntax> !yt \"term1\" \"term2\" \"term3\"")
    elif args == "dd":
        return await pibot.send_message(ctx.message.author,
                                        "This command is used to link Duck Duck Go searches."
                                        "\n\n<syntax> !dd \"term1\" \"term2\" \"term3\"")
    elif args == "py":
        return await pibot.send_message(ctx.message.author,
                                        "This command is used to link Python documentation searches."
                                        "\n\n<syntax> !py \"term1\" \"term2\" \"term3\"")
    elif args == "dpy":
        return await pibot.send_message(ctx.message.author,
                                        "This command is used to link discord.py documentation searches."
                                        "\n\n<syntax> !dpy \"term1\" \"term2\" \"term3\"")
    elif args == "ti":
        return await pibot.send_message(ctx.message.author,
                                        "This command is used to post the local time of the bot (usually pacific)."
                                        "\n\n<syntax> !ti")
    elif args == "wtp":
        return await pibot.send_message(ctx.message.author,
                                        "This command is used to play the Who's that Pokemon game. Players will"
                                        "race to guess Pokemon sillouettes."
                                        "\n\n<syntax> !wtp")
    else:
        return await pibot.send_message(ctx.message.author,
                                        "Invalid help topic. Try using !ls help.")

p = pkmn()
TIME = 15

@pibot.command(pass_context=True)
async def wtp(ctx, *args):
    if not p.LOCK:
        #print(args)
        gen = -1
        if args and len(args) is 1 and args[0].isdigit():
            gen = int(args[0])

        p.initialize(gen=gen)
        print("Who's that Pokemon! ({})".format(p.pkmn_name))
        # display welcome message
        intro_msg = await pibot.say(p.display_message())

        # upload silhouette
        try:
            kuro_img = await pibot.upload(p.display_img(silhouette=True))
            # img = await pibot.send_file(ctx.message.channel, p.display_img(silhouette=True))
        except IsADirectoryError:
            print('Tried to display a directory')
            p.LOCK = False
            return

        def check(msg):
            return msg.author != (bot_name)

        def check_guess(guess):
            guess_str = guess.content.lower()
            if guess_str == p.pkmn_name:
                return True
            else:
                return False

        timer_msg = await pibot.say('You have {} seconds to guess'.format(TIME))
        guess = await pibot.wait_for_message(timeout=TIME, check=check)
        await pibot.delete_messages((intro_msg, kuro_img, timer_msg))

        end_msg = ''
        if guess is None:
            end_msg = 'Time out!'
        elif check_guess(guess):
            end_msg = 'You win!'
        else:
            end_msg = 'You lose!'

        win_msg = await pibot.say("{} It's #{} {}!".format(end_msg,
                                                           p.pkmn_id,
                                                           p.pkmn_name.capitalize()))
        color_img = await pibot.upload(p.display_img(silhouette=False), delete_after=TIME)
        #color_img = await pibot.upload(p.display_img(silhouette=False))

        p.LOCK = False

    else: print("A game is currently in session")
    return


@pibot.command()
async def tw(*args):
    print(args)
    url = ("https://www.twitch.tv/{}".format(args[0]))
    return await pibot.say(url)


@pibot.command()
async def yt(*args):
    print(args)
    url = ("https://www.youtube.com/results?search_{}".format(
        urlencode({'query': ' '.join(args)})))
    return await pibot.say(url, delete_after=10)


@pibot.command()
async def dd(*args):
    print(args)
    url = ("https://duckduckgo.com/?{}".format(
        urlencode({'q': ' '.join(args)})))
    return await pibot.say(url, delete_after=10)


@pibot.command()
async def py(*args):
    print(args)
    url = ("https://docs.python.org/3/search.html?{}"
           "&check_keywords=yes&area=default".format(
        urlencode({'q': ' '.join(args)})))
    return await pibot.say(url, delete_after=10)


@pibot.command()
async def dpy(*args):
    print(args)
    url = ("https://discordpy.readthedocs.io/en/latest/search.html?{}"
           "&check_keywords=yes&area=default".format(
        urlencode({'q': ' '.join(args)})))
    return await pibot.say(url, delete_after=10)


@pibot.command()
async def ti(*args):
    now = datetime.now()
    print(now)
    return await pibot.say("piB0t time is %s:%s:%s PST  %s/%s/%s"
                           % (now.hour, now.minute, now.second, now.month,
                              now.day, now.year), delete_after=10)


pibot.run(secrets.BOT_TOKEN)