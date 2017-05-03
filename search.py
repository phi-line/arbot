import discord
from discord.ext import commands

from urllib.parse import urlencode

class Search():
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def tw(self, *args):
        '''
        Twitch username lookup
        Usage: !tw [username]
        e.g:   !tw phi_liney
        '''
        print(args)
        url = ("https://www.twitch.tv/{}".format(args[0]))
        return await self.bot.say(url)


    @commands.command()
    async def yt(self, *args):
        '''
        YouTube search
        Usage: !yt [query]
        e.g:   !yt cat videos
        '''
        print(args)
        url = ("https://www.youtube.com/results?search_{}".format(
            urlencode({'query': ' '.join(args)})))
        return await self.bot.say(url, delete_after=10)


    @commands.command()
    async def ddg(self, *args):
        '''
        DuckDuckGo search
        Usage: !ddg [query]
        e.g:   !ddg cat pictures
        '''
        print(args)
        url = ("https://duckduckgo.com/?{}".format(
            urlencode({'q': ' '.join(args)})))
        return await self.bot.say(url, delete_after=10)


    @commands.command()
    async def py(self, *args):
        '''
        Python 3 documentation search
        Usage: !py [query]
        e.g:   !py dictionary
        '''
        print(args)
        url = ("https://docs.python.org/3/search.html?{}"
               "&check_keywords=yes&area=default".format(
            urlencode({'q': ' '.join(args)})))
        return await self.bot.say(url, delete_after=10)


    @commands.command()
    async def dpy(self, *args):
        '''
        Discord.py documentation search
        Usage: !dpy [query]
        e.g:   !dpy embed
        '''
        print(args)
        url = ("https://discordpy.readthedocs.io/en/latest/search.html?{}"
               "&check_keywords=yes&area=default".format(
            urlencode({'q': ' '.join(args)})))
        return await self.bot.say(url, delete_after=10)

def setup(bot):
    bot.add_cog(Search(bot))