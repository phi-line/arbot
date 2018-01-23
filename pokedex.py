import discord
from discord.ext import commands

from string import punctuation

from urllib.error import HTTPError
from urllib.request import urlopen

import pokebase as pb
from random import randint

from globals import Globals as g
from pkmnTypes import PkmnTypes as pt
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

    MAX_PKMN = 721

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
            if args and len(args) >= 1:
                t = args[0]
                if type(t) == str and t.startswith('-'):
                    if t in random_args:
                        t = randint(1, Pokedex.MAX_PKMN)
                if '-s' in args[1:] or '-shiny' in args[1:]:
                    shiny = True
                if type(t) == int or type(t) == str:
                    self.lock = True
                    if type(t) == str:
                        t = t.lower()

                    try:
                        species = pb.pokemon_species(t)
                        pokemon = pb.pokemon(t)
                    except ValueError:
                        console_txt = 'Invalid Pokémon: ' + str(t) + ' given'
                        print(console_txt)

                        title = 'What the zzzt?! Invalid Pokémon name / ID'
                        msg = await self.bot.say(embed=rtm.rotom_embed(title,dex_usage))

                        self.lock = False
                        return

                    pkmn_id = species.id
                    pkmn_name = species.name

                    pkmn_genus = species.genera[2].genus
                    pkmn_url = 'https://veekun.com/dex/pokemon/' + pkmn_name
                    # print("Displaying Pokemon {0} #{1}".format(pkmn_name, pkmn_id))

                    filename = self.get_thumbnail(pkmn_id, pkmn_name, shiny=shiny)

                    pkmn_type = [x.type.name for x in pokemon.types]
                    pkmn_abilities = [x.ability.name for x in pokemon.abilities]
                    type_emojis = ' '.join({g.TYPE_DICT[t] for t in pkmn_type if t in g.TYPE_DICT})

                    if shiny: type_emojis += g.S_ICON

                    title = "{0} #{1} {2}".format(pkmn_name.capitalize(), pkmn_id, type_emojis)
                    sub_title = "the {0}".format(pkmn_genus)

                    embed = discord.Embed(title=title, url=pkmn_url, color=g.COLOR)
                    embed.set_thumbnail(url=filename)
                    embed = this.std_embed(embed, species, sub_title)
                    embed = this.type_embed(embed, types=pkmn_type, abilities=pkmn_abilities, sub_title='Type Chart:')

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
    def get_thumbnail(id: int, name: str, shiny=False):
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
                filename = ''.join((g.GIF_URL, s.translate(trans), '.gif'))
            else: filename = ''.join((g.S_GIF_URL, s.translate(trans), '.gif'))
            a = urlopen(filename)
        except HTTPError:
            if not shiny:
                filename = ''.join((g.IMG_URL, str(id), '.png'))
            else: filename = ''.join((g.S_IMG_URL, str(id), '.png'))
        finally:
            return filename

    @staticmethod
    def std_embed(embed: discord.Embed, p: dict, sub_title: str):
        '''
        Takes an embed object as a parameter and then adds pokemon flavor text to it as a new field
        :param embed: discord.Embed
        :param p: pkmn
        :param sub_title: string      - The string to set as the title of the new field
        :return: embed: discord.Embed - A copy of the given embed object with the new field attatched
        '''
        pkmn_desc = [entry for entry in p.flavor_text_entries if entry.language.name == 'en'][0].flavor_text
        pkmn_desc = pkmn_desc.replace('\n', ' ')
        embed.add_field(name=sub_title, value=pkmn_desc)
        return embed

    @staticmethod
    def type_embed(embed: discord.Embed, types: list, abilities: list, sub_title: str):
        '''
        Takes an embed object as a parameter and then adds pokemon type emojis to it as a new field
        :param embed: discord.Embed
        :param type_set: set - containing all the types that this pokemon is
        :param sub_title: string       - The string to set as the title of the new field
        :return: embed: discord.Embed  - A copy of the given embed object with the new field attatched
        '''
        type_dict = pt.combine(t=types, a=abilities)
        msg = pt.format_msg(type_dict)

        embed.add_field(name=sub_title, value=msg)
        return embed

def setup(bot):
    bot.add_cog(Pokedex(bot))
