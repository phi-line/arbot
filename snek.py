'''
Todo: - super effective weakness chart
      - image compression for large art
'''
import re
from random import randint
from datetime import datetime
from string import punctuation

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
avatar = 'arbok.png'

from PokeAPI import PokeAPI
import pokemon
from pokemon import pkmn

@pybot.async_event
async def on_ready():
    print("Logged in as {}".format(bot_name))
    #await pybot.edit_profile(username=bot_name, avatar=open(avatar, 'rb').read())

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

        print("Who's that Pokémon! ({})".format(p.pkmn_name))
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

        p.LOCK = False

    else: print("A game is currently in session")
    return

COLOR = 0xe74c3c
IMG_URL = 'https://veekun.com/dex/media/pokemon/main-sprites/x-y/'
#GIF_URL = 'http://www.pkparaiso.com/imagenes/xy/sprites/animados/'
GIF_URL = 'http://www.pokestadium.com/sprites/xy/'
DEX_URL = 'http://cdn.bulbagarden.net/upload/thumb/3/36/479Rotom-Pok%C3%A9dex.png/160px-479Rotom-Pok%C3%A9dex.png'

DEX_USAGE = "Pokémon must be from Gen I - VI\n" \
              "```Usage: !dex [pkmn # or name]\n" \
              "e.g:   !dex 151 / !dex mew```"

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
                    console_txt = 'Invalid Pokémon: ' + str(t) + ' given'
                    print(console_txt)

                    title = 'What the zzzt?! Invalid Pokémon name / ID'
                    msg = await pybot.say(embed=rotom_embed(title,DEX_USAGE))

                    dx.LOCK = False
                    return

                pkmn_id = pkmn['id']
                pkmn_name = pkmn['name']
                pkmn_genus = pkmn['genera'][0]['genus'] #lang: en
                pkmn_url = 'https://veekun.com/dex/pokemon/' + pkmn_name
                pkmn_desc = pkmn['flavor_text_entries'][1]['flavor_text']

                dx.initialize(id=pkmn_id)

                #print(''.join((GIF_URL, str(pkmn_name), '.gif')))
                try:
                    s = str(pkmn_name)
                    trans = str.maketrans('', '', punctuation)
                    filename = ''.join((GIF_URL, s.translate(trans), '.gif'))
                    a = urlopen(filename)
                except urllib.error.HTTPError:
                    filename = ''.join((IMG_URL, str(pkmn_id), '.png'))

                title = "[#{0}] {1} - the {2} Pokemon:".format(pkmn_id,
                                                               pkmn_name.capitalize(),
                                                               pkmn_genus)
                embed = discord.Embed(title=title, description=pkmn_desc,
                                      url=pkmn_url, color=COLOR)
                embed.set_thumbnail(url=filename)
                msg = await pybot.say(embed=embed)

                dx.LOCK = False
                return
        else:
            title = 'Kzzzzrrt?! Invalid usage! Zzt-zzt!'
            msg = await pybot.say(embed=rotom_embed(title,DEX_USAGE))
            return
    else:
        print("The dex is currently in use")
    return

FUSE_URL = 'http://pokemon.alexonsager.net/{0}/{1}'
FUSE_IMG = 'http://images.alexonsager.net/pokemon/fused/{0}/{0}.{1}.png'
FUSE_USAGE = "Pokémon must be from Gen I only\n" \
              "```Usage: !fuse [pkmn # or name]\n" \
              "e.g:   !fuse abra mew```"

@pybot.command()
async def fuse(p1=None, p2=None):
    '''
    Fuse two Gen I Pokémon together!
    Credits: Alex Onsager - fused images
    Usage: !fuse [pkmn # or name]
    e.g:   !fuse abra mew / !fuse 1 25
    '''

    if p1:
        if p1 == '-r':
            p1 = randint(1,151)
            p2 = randint(1,151)
    if p1 and p2:
        papi = PokeAPI()
        try:
            pkmn_1 = papi.get_pokemon(p1)
            pkmn_2 = papi.get_pokemon(p2)
            if pkmn_1['id'] > 151 or pkmn_2['id'] > 151:
                raise ValueError
        except ValueError:
            console_txt = 'Invalid Pokémon given'
            print(console_txt)

            title = "Zzzrt?! It'zzz an unidentified Pokémon!"
            msg = await pybot.say(embed=rotom_embed(title,FUSE_USAGE))
            return

        pk1_name = pkmn_1['name']; pk2_name = pkmn_2['name']
        title = "Zzz-zzzzt! Fused {0} and {1}!".format(pk1_name.capitalize(),
                                                       pk2_name.capitalize())
        print(title)

        lp1 = len(pk1_name); lp2 = len(pk2_name)
        ratio = (lp1 / lp2)/2
        # print(ratio)
        fuse_name = pk1_name[:int(ratio*lp1)] + pk2_name[int(ratio*lp2):]
        fuse_name = fuse_name.capitalize()
        pk1_genus = papi.get_pokemon_species(p1)['genera'][0]['genus']
        pk2_genus = papi.get_pokemon_species(p2)['genera'][0]['genus']

        desc = "the {0} {1} Pokémon".format(pk1_genus, pk2_genus)

        #url = FUSE_URL.format(pkmn_1['id'], pkmn_2['id'])
        img = FUSE_IMG.format(pkmn_1['id'], pkmn_2['id'])

        # type_set1 = {i['type']['name'].capitalize() for i in pkmn_1['types']}
        # type_set2 = {j['type']['name'].capitalize() for j in pkmn_2['types']}
        # type_str = ' '.join(type_set1.union(type_set2))

        embed = discord.Embed(title='', description=title, color=COLOR)
        embed.add_field(name=fuse_name, value=desc, inline=True)
        embed.set_image(url=img)
        msg = await pybot.say(embed=embed)
    else:
        title = 'Kzzzzrrt?! Invalid usage! Zzt-zzt!'
        msg = await pybot.say(embed=rotom_embed(title, FUSE_USAGE))
    return

def rotom_embed(title='', desc=''):
    embed = discord.Embed(title=title, description=desc, color=COLOR)
    embed.set_thumbnail(url=DEX_URL)
    return embed

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