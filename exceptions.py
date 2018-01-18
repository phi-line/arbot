import discord
from globals import Globals as g

class Rotom():
    @staticmethod
    def rotom_embed(title : str, desc : str):
        '''
        This is a helper method to display a rotom exception embed to the chat
        :param title: str             - The title for the embed
        :param desc: str              - The desc for the embed
        :return: embed: discord.Embed - The embed object
        '''
        embed = discord.Embed(title=title, description=desc, color=g.COLOR)
        embed.set_thumbnail(url=g.DEX_URL)
        return embed