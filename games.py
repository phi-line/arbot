import discord
from discord.ext import commands

import re
from random import randint
import time

from PokeAPI import PokeAPI
from pokemon import pkmn
from exceptions import Rotom as rtm
from globals import Globals as g

class Games():
    COLOR = 0xe74c3c
    TIME = 20000

    def __init__(self, bot):
        self.bot = bot
        self.LOCK = False

    @commands.command(pass_context=True)
    async def wtp(self, ctx, *args):
        '''
        Play 'Who's that Pokemon' game
        Players will race to guess Pokemon sillouettes
        Usage: !wtp (gen #)
        e.g:   !wtp / !wtp 1
        '''
        if not self.LOCK:
            p = pkmn()
            gen = 0
            if args and len(args) is 1 and args[0].isdigit():
                gen = int(args[0])
            p.initialize(gen=gen)

            print("Who's that Pokémon! ({})".format(p.pkmn_name))
            intro_msg = await self.bot.say(p.display_message())

            # upload silhouette
            try:
                kuro_img = await self.bot.upload(p.display_img(silhouette=True))
            except IsADirectoryError:
                print('Tried to display a directory')
                self.LOCK = False
                return

            def check(msg):
                if '#9773' in str(msg.author): return False
                return msg.author != self.bot.user.name and \
                       re.match(r'^\S+$', msg.content) and \
                       not msg.content.startswith('>')

            def check_guess(g):
                if not g: return False
                guess_str = g.content.lower()
                return guess_str == p.pkmn_name

            def get_time():
                return int(round(time.time() * 1000))

            end_msg = ''

            timer_msg = await self.bot.say('You have {} seconds to guess'.format(int(Games.TIME/1000)))
            start_time = get_time()

            timeout = 0
            while timeout < Games.TIME:
                diff = (Games.TIME - timeout) / 1000
                await self.bot.edit_message(timer_msg, new_content='You have {:.2f} seconds to guess'.format(diff))
                guess = await self.bot.wait_for_message(timeout=diff, check=check)
                if check_guess(guess):
                    end_msg = 'You win!'
                    break
                else:
                    timeout = get_time() - start_time
                    diff = (Games.TIME - timeout)/1000

                    end_msg = 'You Lose!'

            g.IS_BOT and await self.bot.delete_messages((intro_msg, kuro_img, timer_msg))

            win_msg = await self.bot.say("{} It's #{} {}!".format(end_msg,
                                                                  p.pkmn_id,
                                                                  p.pkmn_name.capitalize()))
            color_img = await self.bot.upload(p.display_img(silhouette=False))
            self.LOCK = False

        else: print("A game is currently in session")
        return

    FUSE_URL = 'http://pokemon.alexonsager.net/{0}/{1}'
    FUSE_IMG = 'http://images.alexonsager.net/pokemon/fused/{0}/{0}.{1}.png'
    FUSE_USAGE = "Pokémon must be from Gen I only\n" \
                 "```Arg  : Random Pokemon '-r'\n" \
                 "Usage: {0}fuse [p1] [p2] / {0}fuse -r\n" \
                 "e.g  : {0}fuse arbok ditto / {0}fuse ditto 25\n" \
                 "       {0}fuse -r pikachu / {0}fuse 132 -r```"

    CLARENCE = 'https://raw.githubusercontent.com/phi-line/arbot/master/clarence.png'


    @commands.command()
    async def fuse(self, p1=None, p2=None):
        '''
        Fuse two Gen I Pokémon together!
        Credits: Alex Onsager - fused images
        Usage: !fuse [pkmn # or name]
        e.g:   !fuse abra mew / !fuse 1 25
        '''
        from games import Games as this
        fuse_usage = this.FUSE_USAGE.format(self.bot.command_prefix)
        random_args = ['-r', '-rand', '-random']; r = False
        if p1.lower() == 'clarence':
            embed = discord.Embed(title='be strong clarence', description='be strong for mother', color=g.COLOR)
            embed.set_image(url=Games.CLARENCE)
            msg = await self.bot.say(embed=embed)
            return
        if p1 and not p2:
            if p1 in random_args:
                p1 = randint(1,151)
                p2 = randint(1,151)
                r = True
        if p1 and p2:
            if not r and (p1 in random_args or p2 in random_args):
                if p1 in random_args:
                    p1 = randint(1,151)
                if p2 in random_args:
                    p2 = randint(1,151)

            papi = PokeAPI()
            try:
                pkmn_1 = papi.get_pokemon(p1)
                pkmn_2 = papi.get_pokemon(p2)
                if pkmn_1['id'] > 151 or pkmn_2['id'] > 151:
                    raise ValueError
            except ValueError:
                console_txt = 'Invalid Pokémon given: {0} and {1}'.format(p1, p2)
                print(console_txt)

                title = "Zzzrt?! It'zzz an unidentified Pokémon!"
                msg = await self.bot.say(embed=rtm.rotom_embed(title,fuse_usage))
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
            pk1_genus = papi.get_pokemon_species(p1)['genera'][2]['genus']
            pk1_genus = pk1_genus.split()[:-1]
            pk1_genus = ''.join(pk1_genus)
            pk2_genus = papi.get_pokemon_species(p2)['genera'][2]['genus']

            desc = "the {0} {1}".format(pk1_genus, pk2_genus)

            #url = FUSE_URL.format(pkmn_1['id'], pkmn_2['id'])
            img = this.FUSE_IMG.format(pkmn_1['id'], pkmn_2['id'])

            type_set = {i['type']['name'] for i in pkmn_1['types']}
            type_set2 = {j['type']['name'] for j in pkmn_2['types']}
            type_set = type_set.union(type_set2)
            type_str = ' '.join([g.TYPE_DICT[i] for i in type_set if i in g.TYPE_DICT])

            sub_title = '{0} {1}'.format(fuse_name, type_str)

            embed = discord.Embed(title='', description=title, color=g.COLOR)
            embed.add_field(name=sub_title, value=desc, inline=True)
            embed.set_image(url=img)
            msg = await self.bot.say(embed=embed)
        else:
            title = 'Kzzzzrrt?! Invalid usage! Zzt-zzt!'
            msg = await self.bot.say(embed=rtm.rotom_embed(title, fuse_usage))
        return

def setup(bot):
    bot.add_cog(Games(bot))
