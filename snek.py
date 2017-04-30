'''
Todo: - super effective weakness chart
      - image compression for large art
'''
import os, re
from os.path import isfile, join, dirname, abspath
from datetime import datetime
from urllib.parse import urlencode

import discord
from discord.ext import commands
from discord.ext.commands import Bot
import secrets

client = discord.Client()
pybot = Bot(command_prefix="!")
# pybot = commands.Bot(command_prefix='!')
bot_name = 'arbot'

import pokemon
from pokemon import pkmn
# import flickrapi
#
# api_key = u'989932649fe52a7cb564acde5f047022'
# api_secret = u'cf37ae39f0590480'
#
# flickr = flickrapi.FlickrAPI(api_key, api_secret)
# flickr.authenticate_via_browser(perms='delete')

@pybot.async_event
async def on_ready():
    print("Logged in as {}".format(bot_name))
    await pybot.edit_profile(username=bot_name)

@pybot.command(pass_context=True)
async def ls(ctx, *, args):
    print(args)
    print(len(args))
    if args == "help":
        return await pybot.send_message(ctx.message.author,
                                        "Command list: !tw !yt !dd !py !dpy !ti !pyg"
                                        "\n\nType !ls \"command\" for help on that topic.")
    elif args == "tw":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to link a twitch user's stream."
                                        "\n\n<syntax> !tw \"username\"")
    elif args == "yt":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to link youtube searches."
                                        "\n\n<syntax> !yt \"term1\" \"term2\" \"term3\"")
    elif args == "dd":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to link Duck Duck Go searches."
                                        "\n\n<syntax> !dd \"term1\" \"term2\" \"term3\"")
    elif args == "py":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to link Python documentation searches."
                                        "\n\n<syntax> !py \"term1\" \"term2\" \"term3\"")
    elif args == "dpy":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to link discord.py documentation searches."
                                        "\n\n<syntax> !dpy \"term1\" \"term2\" \"term3\"")
    elif args == "ti":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to post the local time of the bot (usually pacific)."
                                        "\n\n<syntax> !ti")
    elif args == "wtp":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to play the Who's that Pokemon game. Players will "
                                        "race to guess Pokemon sillouettes."
                                        "\n\n<syntax> !wtp (gen #)")
    elif args == "dex":
        return await pybot.send_message(ctx.message.author,
                                        "This command is used to give dex info about the Pokemon"
                                        "\n\n<syntax> !dex [pknn #] / [pkmn name]")
    else:
        return await pybot.send_message(ctx.message.author,
                                        "Invalid help topic. Try using !ls help.")


TIME = 15

@pybot.command(pass_context=True)
async def wtp(ctx, *args):
    p = pkmn()
    if not p.LOCK:
        gen = 0
        if args and len(args) is 1 and args[0].isdigit():
            gen = int(args[0])
        p.initialize(gen=gen)

        print("Who's that Pokemon! ({})".format(p.pkmn_name))
        intro_msg = await pybot.say(p.display_message())

        # upload silhouette
        try:
            kuro_img = await pybot.upload(p.display_img(silhouette=True))
            # img = await pybot.send_file(ctx.message.channel, p.display_img(silhouette=True))
        except IsADirectoryError:
            print('Tried to display a directory')
            p.LOCK = False
            return

        def check(msg):
            return msg.author != (bot_name) and \
                   re.match(r'^\S+$', msg.content) and \
                   not msg.content.startswith('!')

        def check_guess(guess):
            guess_str = guess.content.lower()
            return guess_str == p.pkmn_name

        timer_msg = await pybot.say('You have {} seconds to guess'.format(TIME))
        guess = await pybot.wait_for_message(timeout=TIME, check=check)
        await pybot.delete_messages((intro_msg, kuro_img, timer_msg))

        end_msg = ''
        if guess is None:
            end_msg = 'Time out!'
        elif check_guess(guess):
            end_msg = 'You win!'
        else:
            end_msg = 'You lose!'

        win_msg = await pybot.say("{} It's #{} {}!".format(end_msg,
                                                           p.pkmn_id,
                                                           p.pkmn_name.capitalize()))
        color_img = await pybot.upload(p.display_img(silhouette=False), delete_after=TIME)
        #color_img = await pybot.upload(p.display_img(silhouette=False))

        p.LOCK = False

    else: print("A game is currently in session")
    return

COLOR = 0xe74c3c
IMG_URL = 'https://veekun.com/dex/media/pokemon/main-sprites/x-y/'

@pybot.command(pass_context=True)
async def dex(ctx, *args):
    pkmn_id = 0; pkmn_name = ''; pkmn_genus = ''; pkmn_desc = ''
    p = pokemon.pkmn()
    if not p.LOCK:
        #pokemon number given
        if args and len(args) == 1:
            t = args[0]
            if type(t) == int or type(t) == str:
                p.LOCK = True
                if type(t) == str:
                    t = t.lower()

                pkmn = p.papi.get_pokemon_species(t)
                pkmn_id = pkmn['id']
                pkmn_name = pkmn['name']
                pkmn_genus = pkmn['genera'][0]['genus'] #lang: en
                pkmn_url = 'https://veekun.com/dex/pokemon/' + pkmn_name

                pkmn_desc = pkmn['flavor_text_entries'][1]['flavor_text']

                # https://veekun.com/dex/pokemon/bulbasaur

                p.initialize(id=pkmn_id)

                title = "[#{0}] {1} - the {2} Pokemon:".format(pkmn_id,
                                                               pkmn_name.capitalize(),
                                                               pkmn_genus)

                #color_img = await pybot.upload(p.display_img())

                filename = ''.join((IMG_URL, str(pkmn_id), '.png'))
                embed = discord.Embed(title=title,
                                       description=pkmn_desc,
                                       url=pkmn_url ,
                                       color=COLOR,)
                embed.set_thumbnail(url=filename)

                msg =  await pybot.say(embed=embed)

                p.LOCK = False
    else:
        print("The dex is currently in use")
    return



@pybot.command()
async def tw(*args):
    print(args)
    url = ("https://www.twitch.tv/{}".format(args[0]))
    return await pybot.say(url)


@pybot.command()
async def yt(*args):
    print(args)
    url = ("https://www.youtube.com/results?search_{}".format(
        urlencode({'query': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def dd(*args):
    print(args)
    url = ("https://duckduckgo.com/?{}".format(
        urlencode({'q': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def py(*args):
    print(args)
    url = ("https://docs.python.org/3/search.html?{}"
           "&check_keywords=yes&area=default".format(
        urlencode({'q': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def dpy(*args):
    print(args)
    url = ("https://discordpy.readthedocs.io/en/latest/search.html?{}"
           "&check_keywords=yes&area=default".format(
        urlencode({'q': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def ti(*args):
    now = datetime.now()
    print(now)
    return await pybot.say("piB0t time is %s:%s:%s PST  %s/%s/%s"
                           % (now.hour, now.minute, now.second, now.month,
                              now.day, now.year), delete_after=10)


pybot.run(secrets.BOT_TOKEN)