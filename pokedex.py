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
                "e.g  : {0}dex 151 / {0}dex mew\n" \
                "       {0}dex -random -shiny```"

    @commands.command(pass_context=True)
    async def dex(self, ctx, *args):
        '''
        PokeDex entry for any PKMN
        Usage: !dex [pkmn # or name]
        e.g:   !dex 151 / !dex mew
        '''
        from pokedex import Pokedex as this
        dex_usage = this.DEX_USAGE.format(self.bot.command_prefix)
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
                        pt = papi.get_pokemon(t)
                    except ValueError:
                        console_txt = 'Invalid Pokémon: ' + str(t) + ' given'
                        print(console_txt)

                        title = 'What the zzzt?! Invalid Pokémon name / ID'
                        msg = await self.bot.say(embed=rtm.rotom_embed(title,dex_usage))

                        self.lock = False
                        return

                    pkmn_id = p['id']
                    pkmn_name = p['name']
                    pkmn_genus =  p['genera'][2]['genus'] #lang: en
                    pkmn_url = 'https://veekun.com/dex/pokemon/' + pkmn_name
                    pkmn_type = {i['type']['name'] for i in pt['types']}
                    # print("Displaying Pokemon {0} #{1}".format(pkmn_name, pkmn_id))

                    filename = self.get_thumbnail(pkmn_id, pkmn_name, shiny=shiny)

                    type_emojis = ' '.join({g.TYPE_DICT[t] for t in pkmn_type if t in g.TYPE_DICT})
                    if shiny: type_emojis += g.S_ICON

                    title = "{0} #{1} {2}".format(pkmn_name.capitalize(), pkmn_id, type_emojis)
                    sub_title = "the {0}".format(pkmn_genus)

                    embed = discord.Embed(title=title, url=pkmn_url, color=g.COLOR)
                    embed.set_thumbnail(url=filename)
                    embed = this.std_embed(embed, p, sub_title)
                    embed = this.type_embed(embed, type_set=pkmn_type, sub_title='Type Chart:')

                    msg = await self.bot.say(embed=embed)

                    self.lock = False
                    return
            else:
                title = 'Kzzzzrrt?! Invalid usage! Zzt-zzt!'
                msg = await self.bot.say(embed=rtm.rotom_embed(title,dex_usage))
                return
        else:
            print("The dex is currently in use")
        return

    @staticmethod
    def get_thumbnail(id : int, name : str, shiny=False):
        '''
        This function returns a hotlink of the Pokemon's
        :param id: int     - the pokemon's id
        :param name: str   - the pokemon's name
        :param shiny: bool - get shiny thumbnail?
        :return: filename: string - hotlink of the requested thumbnail
        '''
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
    def std_embed(embed : discord.Embed, p : pkmn, sub_title : str):
        '''
        Takes an embed object as a parameter and then adds pokemon flavor text to it as a new field
        :param embed: discord.Embed
        :param p: pkmn
        :param sub_title: string      - The string to set as the title of the new field
        :return: embed: discord.Embed - A copy of the given embed object with the new field attatched
        '''
        pkmn_desc = p['flavor_text_entries'][2]['flavor_text'].replace('\n', ' ')
        embed.add_field(name=sub_title, value=pkmn_desc)
        return embed

    @staticmethod
    def type_embed(embed : discord.Embed, type_set : set, sub_title : str):
        '''
        Takes an embed object as a parameter and then adds pokemon type emojis to it as a new field
        :param embed: discord.Embed
        :param type_set: set - containing all the types that this pokemon is
        :param sub_title: string       - The string to set as the title of the new field
        :return: embed: discord.Embed  - A copy of the given embed object with the new field attatched
        '''

        #first get all the type info for the pokemon
        #for each type generate Weakness chart
        p = PokeAPI()
        z = dict()
        for t in type_set:
            j = p.get_type(t)
            y = {dt: [val['name'] for val in vals] for dt, vals in j['damage_relations'].items() \
                 if 'from' in str(dt)}
            y = {k: v for k, v in y.items() if v}
            z.update(y)

        builder = ''
        for key in y:
            builder += '{0}: {1}\n'.format(key.replace('_', ' '),
                                         ' '.join({g.TYPE_DICT[t] for t in y[key] if t in g.TYPE_DICT}))

        embed.add_field(name=sub_title, value=builder)
        return embed

def setup(bot):
    bot.add_cog(Pokedex(bot))