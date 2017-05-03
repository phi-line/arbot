import discord
from discord.ext import commands

from string import punctuation

from urllib.error import HTTPError
from urllib.request import urlopen

from PokeAPI import PokeAPI
from pokemon import pkmn as pkmn
from globals import Globals as g
from exceptions import Rotom as rtm

class Pokedex():
    def __init__(self, bot):
        self.bot = bot
        self.lock = False

    DEX_USAGE = "Pokémon must be from Gen I - VI\n" \
                "```Usage: !dex [pkmn # or name]\n" \
                "e.g:   !dex 151 / !dex mew```"

    @commands.command(pass_context=True)
    async def dex(self, ctx, *args):
        '''
        PokeDex entry for any PKMN
        Usage: !dex [pkmn # or name]
        e.g:   !dex 151 / !dex mew
        '''
        from pokedex import Pokedex as this
        pkmn_id = 0; pkmn_name = ''; pkmn_genus = ''; pkmn_url = ''; pkmn_desc = '';
        papi = PokeAPI()
        if not self.lock:
            #pokemon number given
            if args and len(args) == 1:
                t = args[0]
                if type(t) == int or type(t) == str:
                    self.lock = True
                    if type(t) == str:
                        t = t.lower()

                    try:
                        #print("Generating PokeAPI")
                        p = papi.get_pokemon_species(t)
                        pt = papi.get_pokemon(t)['types']
                    except ValueError:
                        console_txt = 'Invalid Pokémon: ' + str(t) + ' given'
                        print(console_txt)

                        title = 'What the zzzt?! Invalid Pokémon name / ID'
                        msg = await self.bot.say(embed=rtm.rotom_embed(title,this.DEX_USAGE))

                        self.lock = False
                        return

                    pkmn_id = p['id']
                    pkmn_name = p['name']
                    pkmn_genus =  p['genera'][0]['genus'] #lang: en
                    pkmn_url = 'https://veekun.com/dex/pokemon/' + pkmn_name
                    pkmn_desc = p['flavor_text_entries'][1]['flavor_text']
                    pkmn_type = {i['type']['name'] for i in pt}
                    print("Displaying Pokemon {0} #{1}".format(pkmn_name, pkmn_id))

                    try:
                        s = str(pkmn_name)
                        trans = str.maketrans('', '', punctuation)
                        filename = ''.join((g.GIF_URL, s.translate(trans), '.gif'))
                        a = urlopen(filename)
                    except HTTPError:
                        filename = ''.join((g.IMG_URL, str(pkmn_id), '.png'))

                    type_emojis = '  '.join({g.TYPE_DICT[t] for t in pkmn_type if t in g.TYPE_DICT})
                    title = "{0} #{1} {2}".format(pkmn_name.capitalize(), pkmn_id, type_emojis)
                    sub_title = "the {0} Pokémon".format(pkmn_genus)
                    embed = discord.Embed(title=title, url=pkmn_url, color=g.COLOR)
                    embed.add_field(name=sub_title, value=pkmn_desc)
                    embed.set_thumbnail(url=filename)

                    msg = await self.bot.say(embed=embed)

                    self.lock = False
                    return
            else:
                title = 'Kzzzzrrt?! Invalid usage! Zzt-zzt!'
                msg = await self.bot.say(embed=rtm.rotom_embed(title,this.DEX_USAGE))
                return
        else:
            print("The dex is currently in use")
        return

def setup(bot):
    bot.add_cog(Pokedex(bot))