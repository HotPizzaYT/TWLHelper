import discord
import hashlib
import feedparser
import os

from discord.ext import tasks, commands
from inspect import cleandoc

import settings


class RSS(commands.Cog):
    """RSS feeds"""

    def __init__(self, bot):
        self.bot = bot
        self.loop.start()

    @tasks.loop(seconds=3600)
    async def loop(self):
        await self.bot.wait_until_ready()
        if settings.NINUPDATE:
            await self.ninupdates()

    async def ninupdates(self):
        async with self.bot.session.get('https://yls8.mtheall.com/ninupdates/feed.php') as resp:
            raw_bytes = await resp.read()

        if not os.path.isfile('ninupdates.xml'):
            new = open('ninupdates.xml', 'wb')
            new.write(raw_bytes)
            new.close()

        f = open('ninupdates.xml', 'rb')
        digestprev = hashlib.sha256(f.read()).digest()
        digestnext = hashlib.sha256(raw_bytes).digest()
        if digestprev == digestnext:
            return
        f.close()

        consoles = [
            'Old3DS',
            'New3DS'
        ]

        f = open('ninupdates.xml', 'r')
        ninupdates_feed = feedparser.parse(raw_bytes)
        ninupdates_old = feedparser.parse(f.read())
        for entry in ninupdates_feed['entries']:
            system, ver = entry['title'].split()
            if system not in consoles:
                continue
            for entryold in ninupdates_old['entries']:
                systemold, verold = entryold['title'].split()
                if systemold not in consoles:
                    continue
                elif system == systemold and ver != verold:
                    channel = self.bot.get_channel(settings.NINUPDATE)
                    await channel.send(embed=discord.Embed(description=cleandoc('ℹ️ New update version for {}: [{}]({})'.format(system, ver, entry['link']))))
                    continue
        f.close()
        f = open('ninupdates.xml', 'wb')
        f.write(raw_bytes)


def setup(bot):
    bot.add_cog(RSS(bot))