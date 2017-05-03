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
                "```Args :\n" \
                "Random Pokémon -r / -random\n" \
                "Shiny  Pokémon -s / -shiny\n\n" \
                "Usage: {0}dex [p1] / '-r' ('-s')\n" \
                "e.g:   {0}dex 151 / {0}dex mew\n" \
                "       {0}dex -random -shiny```"
    DEX_USAGE.format('>')

    @commands.command(pass_context=True)
    async def dex(self, ctx, *args):
        '''
        PokeDex entry for any PKMN
        Usage: !dex [pkmn # or name]
        e.g:   !dex 151 / !dex mew
        '''
        from pokedex import Pokedex as this
        pkmn_id = 0; pkmn_name = ''; pkmn_genus = ''; pkmn_url = ''; pkmn_desc = '';
        random_args = ['-r', '-rand', '-random']
        shiny = False

        if not self.lock:
            papi = PokeAPI()
            if args and len(args) >= 1:
                t = args[0]
                if type(t) == str and t.startswith('-'):
                    if t in random_args:
                        p = pkmn()
                        p.initialize()
                        t = p.pkmn_id
                if '-s' in args[1:] or '-shiny' in args[1:]:
                    shiny = True
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
                    pkmn_type = {i['type']['name'] for i in pt}
                    #print("Displaying Pokemon {0} #{1}".format(pkmn_name, pkmn_id))

                    filename = self.get_thumbnail(pkmn_id, pkmn_name, shiny=shiny)

                    type_emojis = '  '.join({g.TYPE_DICT[t] for t in pkmn_type if t in g.TYPE_DICT})
                    if shiny: type_emojis += g.S_ICON

                    title = "{0} #{1} {2}".format(pkmn_name.capitalize(), pkmn_id, type_emojis)
                    sub_title = "the {0} Pokémon".format(pkmn_genus)

                    embed = discord.Embed(title=title, url=pkmn_url, color=g.COLOR)
                    embed.set_thumbnail(url=filename)
                    embed = this.std_embed(embed, p, sub_title)

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

    @staticmethod
    def get_thumbnail(id, name, shiny=False):
        filename = ''
        try:
            s = str(name)
            trans = str.maketrans('', '', punctuation)
            if not shiny:
                filename =   ''.join((g.GIF_URL, s.translate(trans), '.gif'))
            else: filename = ''.join((g.S_GIF_URL, s.translate(trans), '.gif'))
            a = urlopen(filename)
        except HTTPError:
            if not shiny:
                filename =   ''.join((g.IMG_URL, str(id), '.png'))
            else: filename = ''.join((g.S_IMG_URL, str(id), '.png'))
        finally:
            return filename

    #use for standard picture
    @staticmethod
    def std_embed(embed=discord.Embed, p=pkmn(), sub_title=''):
        pkmn_desc = p['flavor_text_entries'][1]['flavor_text']
        embed.add_field(name=sub_title, value=pkmn_desc)
        return embed

    @staticmethod
    def type_embed():
        pass

def setup(bot):
    bot.add_cog(Pokedex(bot))