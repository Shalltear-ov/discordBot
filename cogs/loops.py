from disnake.ext import commands, tasks
import time
from Userform import User, EMBED_CLASS
import disnake
from random import choice
from View import Git_away
from config import SETTING


class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @tasks.loop(seconds=5)
    async def git_away(self):
        channels = self.bot.get_guild(SETTING['GUILD_ID']).text_channels
        channel: disnake.TextChannel = choice(channels)
        view = Git_away()
        disnake.message.Message = await channel.send(view=view, delete_after=5)

    @commands.slash_command(name='git_away', description='get your balance', guild_ids=[SETTING['GUILD_ID']])
    async def start(self, ctx):
        self.git_away.start()
        await ctx.send("started git_away")


def setup(bot):
    bot.add_cog(Loops(bot))
