import discord
from discord.ext import commands

from string import punctuation

from urllib.error import HTTPError
from urllib.request import urlopen

from pokemon import pkmn as pkmn
from globals import Globals as g
from exceptions import Rotom as rtm

class Pokedex():
    def __init__(self, bot):
        self.bot = bot

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
        dx = pkmn()
        if not dx.LOCK:
            #pokemon number given
            if args and len(args) == 1:
                t = args[0]
                if type(t) == int or type(t) == str:
                    dx.LOCK = True
                    if type(t) == str:
                        t = t.lower()

                    try:
                        p = dx.papi.get_pokemon_species(t)
                    except ValueError:
                        console_txt = 'Invalid Pokémon: ' + str(t) + ' given'
                        print(console_txt)

                        title = 'What the zzzt?! Invalid Pokémon name / ID'
                        msg = await self.bot.say(embed=rtm.rotom_embed(title,this.DEX_USAGE))

                        dx.LOCK = False
                        return

                    pkmn_id = p['id']
                    pkmn_name = p['name']
                    pkmn_genus = p['genera'][0]['genus'] #lang: en
                    pkmn_url = 'https://veekun.com/dex/pokemon/' + pkmn_name
                    pkmn_desc = p['flavor_text_entries'][1]['flavor_text']

                    dx.initialize(id=pkmn_id)

                    #print(''.join((GIF_URL, str(pkmn_name), '.gif')))
                    try:
                        s = str(pkmn_name)
                        trans = str.maketrans('', '', punctuation)
                        filename = ''.join((g.GIF_URL, s.translate(trans), '.gif'))
                        a = urlopen(filename)
                    except HTTPError:
                        filename = ''.join((g.IMG_URL, str(pkmn_id), '.png'))

                    title = "[#{0}] {1} - the {2} Pokemon:".format(pkmn_id,
                                                                   pkmn_name.capitalize(),
                                                                   pkmn_genus)
                    embed = discord.Embed(title=title, description=pkmn_desc,
                                          url=pkmn_url, color=g.COLOR)
                    embed.set_thumbnail(url=filename)
                    msg = await self.bot.say(embed=embed)

                    dx.LOCK = False
                    return
            else:
                title = 'Kzzzzrrt?! Invalid usage! Zzt-zzt!'
                msg = await self.bot.say(embed=rtm.rotom_embed(title,g=this.DEX_USAGE))
                return
        else:
            print("The dex is currently in use")
        return

def setup(bot):
    bot.add_cog(Pokedex(bot))