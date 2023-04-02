from disnake.ext import commands, tasks
import time
from Userform import User, EMBED_CLASS
import disnake
from random import choice
from View import Git_away
from config import SETTING
from PIL import Image, ImageDraw, ImageFont


async def draw_banner(num):
    img = Image.open("banner.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial", 100)
    x, y = img.size
    _, _, xb, yb = draw.textbbox((0, 0), f"{num}", font=font)
    draw.text(((x-xb)/2, (y-yb)/2), f"{num}", font=font)
    img.save("result_banner.png")


class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @tasks.loop(seconds=3000)
    async def git_away(self):
        channels = self.bot.get_guild(SETTING['GUILD_ID']).text_channels
        channel: disnake.TextChannel = choice(channels)
        view = Git_away()
        disnake.message.Message = await channel.send(view=view, delete_after=5)

    @commands.slash_command(name='git_away', description='get your balance', guild_ids=[SETTING['GUILD_ID']])
    async def start_git_away(self, ctx):
        if self.git_away.is_running():
            self.git_away.stop()
            await ctx.send("stoped git_away")
            return
        self.git_away.start()
        await ctx.send("started git_away")

    @commands.slash_command(name='banner', description='get your balance', guild_ids=[SETTING['GUILD_ID']])
    async def start_draw_banner(self, ctx):
        if self.draw_banner.is_running():
            self.draw_banner.stop()
            await ctx.send("stoped draw_banner")
            return
        self.draw_banner.start()
        await ctx.send("started draw_banner")

    @tasks.loop(seconds=60)
    async def draw_banner(self):
        guild = self.bot.get_guild(SETTING['GUILD_ID'])
        count_members = 0
        for voice in guild.voice_channels:
            count_members += len(voice.members)
        await draw_banner(count_members)
        embed = EMBED_CLASS().image_embed("result_banner.png")
        channel: disnake.TextChannel = self.bot.get_guild(SETTING['GUILD_ID']).get_channel(972208614251053087)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Loops(bot))
