import discord
from discord.ext import commands

import re
from random import randint

from PokeAPI import PokeAPI
from pokemon import pkmn
from exceptions import Rotom as rtm
from globals import Globals as g

class Games():
    COLOR = 0xe74c3c
    TIME = 15

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
                return msg.author != (self.bot.user.name) and \
                       re.match(r'^\S+$', msg.content) and \
                       not msg.content.startswith('!')

            def check_guess(guess):
                guess_str = guess.content.lower()
                return guess_str == p.pkmn_name

            timer_msg = await self.bot.say('You have {} seconds to guess'.format(Games.TIME))
            guess = await self.bot.wait_for_message(timeout=Games.TIME, check=check)
            await self.bot.delete_messages((intro_msg, kuro_img, timer_msg))

            end_msg = ''
            if guess is None:
                end_msg = 'Time out!'
            elif check_guess(guess):
                end_msg = 'You win!'
            else:
                end_msg = 'You lose!'

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
                 "Use arg '-r' to randomly fuse two Pokémon\n" \
                 "```Usage: !fuse [p1] [p2] / !fuse -r\n" \
                 "e.g:   !fuse abra mew / !fuse ditto 25```"

    @commands.command()
    async def fuse(self, p1=None, p2=None):
        '''
        Fuse two Gen I Pokémon together!
        Credits: Alex Onsager - fused images
        Usage: !fuse [pkmn # or name]
        e.g:   !fuse abra mew / !fuse 1 25
        '''
        from games import Games as this
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
                msg = await self.bot.say(embed=rtm.rotom_embed(title,this.FUSE_USAGE))
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
            msg = await self.bot.say(embed=rtm.rotom_embed(title, this.FUSE_USAGE))
        return

def setup(bot):
    bot.add_cog(Games(bot))