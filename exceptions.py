import discord
import globals as g

class Rotom():

    @staticmethod
    def rotom_embed(title='', desc=''):
        embed = discord.Embed(title=title, description=desc, color=g.COLOR)
        embed.set_thumbnail(url=globals.DEX_URL)
        return embed