import discord
from globals import Globals as g

class Rotom():

    @staticmethod
    def rotom_embed(title='', desc=''):
        embed = discord.Embed(title=title, description=desc, color=g.COLOR)
        embed.set_thumbnail(url=g.DEX_URL)
        return embed