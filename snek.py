'''
Todo: - super effective weakness chart
      - image compression for large art
'''
import os, re
from os.path import isfile, join, dirname, abspath
from random import randrange
from datetime import datetime

import urllib.error
from urllib.parse import urlencode
from urllib.request import urlopen

import discord
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

TIME = 15
p = pkmn()

@pybot.command(pass_context=True)
async def wtp(ctx, *args):
    '''
    Play 'Who's that Pokemon' game
    Players will race to guess Pokemon sillouettes
    Usage: !wtp (gen #)
    e.g:   !wtp / !wtp 1
    '''
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
GIF_URL = 'http://www.pkparaiso.com/imagenes/xy/sprites/animados/'
DEX_URL = 'http://cdn.bulbagarden.net/upload/9/98/Key_Rotom_Pok%C3%A9dex_Sprite.png'

@pybot.command(pass_context=True)
async def dex(ctx, *args):
    '''
    PokeDex entry for any PKMN
    Usage: !dex [pkmn # or name]
    e.g:   !dex 151 / !dex mew
    '''
    pkmn_id = 0; pkmn_name = ''; pkmn_genus = ''; pkmn_url = ''; pkmn_desc = ''
    dx = pokemon.pkmn()
    if not dx.LOCK:
        #pokemon number given
        if args and len(args) == 1:
            t = args[0]
            if type(t) == int or type(t) == str:
                dx.LOCK = True
                if type(t) == str:
                    t = t.lower()

                try:
                    pkmn = dx.papi.get_pokemon_species(t)
                except ValueError:
                    console_txt = 'Invalid Pokemon: ' + str(t) + ' given'
                    print(console_txt)

                    title = 'What the zzzt?! invalid Pokemon name / ID'
                    desc = "Pokemon must be from Gen I - VI\n"\
                           "```Usage: !dex [pkmn # or name]\n"\
                           "e.g:   !dex 151 / !dex mew```"

                    embed = discord.Embed(title=title, description=desc, color=COLOR)
                    embed.set_thumbnail(url=DEX_URL)
                    msg = await pybot.say(embed=embed)

                    dx.LOCK = False
                    return

                pkmn_id = pkmn['id']
                pkmn_name = pkmn['name']
                pkmn_genus = pkmn['genera'][0]['genus'] #lang: en
                pkmn_url = 'https://veekun.com/dex/pokemon/' + pkmn_name

                pkmn_desc = pkmn['flavor_text_entries'][1]['flavor_text']
                # pkmn_desc_list= pkmn['flavor_text_entries']
                # pkmn_desc_en = [i for i in [j for j in range(len(pkmn_desc_list))]\
                #                if pkmn_desc_list[i]['language']['name'] == 'en']
                # en_i = pkmn_desc_en[randrange(0, len(pkmn_desc_en))]
                # pkmn_desc = pkmn['flavor_text_entries'][en_i]['flavor_text']

                # https://veekun.com/dex/pokemon/bulbasaur

                dx.initialize(id=pkmn_id)

                title = "[#{0}] {1} - the {2} Pokemon:".format(pkmn_id,
                                                               pkmn_name.capitalize(),
                                                               pkmn_genus)

                #color_img = await pybot.upload(p.display_img())

                try:
                    filename = ''.join((GIF_URL, str(pkmn_name), '.gif'))
                    a = urlopen(filename)
                except urllib.error.HTTPError:
                    filename = ''.join((IMG_URL, str(pkmn_id), '.png'))

                embed = discord.Embed(title=title,
                                       description=pkmn_desc,
                                       url=pkmn_url ,
                                       color=COLOR,)
                embed.set_thumbnail(url=filename)

                msg =  await pybot.say(embed=embed)

                dx.LOCK = False
    else:
        print("The dex is currently in use")
    return

@pybot.command()
async def tw(*args):
    '''
    Twitch username lookup
    Usage: !tw [username]
    e.g:   !tw phi_liney
    '''
    print(args)
    url = ("https://www.twitch.tv/{}".format(args[0]))
    return await pybot.say(url)


@pybot.command()
async def yt(*args):
    '''
    YouTube search
    Usage: !yt [query]
    e.g:   !yt cat videos
    '''
    print(args)
    url = ("https://www.youtube.com/results?search_{}".format(
        urlencode({'query': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def ddg(*args):
    '''
    DuckDuckGo search
    Usage: !ddg [query]
    e.g:   !ddg cat pictures
    '''
    print(args)
    url = ("https://duckduckgo.com/?{}".format(
        urlencode({'q': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def py(*args):
    '''
    Python 3 documentation search
    Usage: !py [query]
    e.g:   !py dictionary
    '''
    print(args)
    url = ("https://docs.python.org/3/search.html?{}"
           "&check_keywords=yes&area=default".format(
        urlencode({'q': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def dpy(*args):
    '''
    Discord.py documentation search
    Usage: !dpy [query]
    e.g:   !dpy embed
    '''
    print(args)
    url = ("https://discordpy.readthedocs.io/en/latest/search.html?{}"
           "&check_keywords=yes&area=default".format(
        urlencode({'q': ' '.join(args)})))
    return await pybot.say(url, delete_after=10)


@pybot.command()
async def ti():
    '''
    Display the bot's time (PST)
    Usage: !ti
    '''
    now = datetime.now()
    print(now)
    return await pybot.say("piB0t time is %s:%s:%s PST  %s/%s/%s"
                           % (now.hour, now.minute, now.second, now.month,
                              now.day, now.year), delete_after=10)


pybot.run(secrets.BOT_TOKEN)