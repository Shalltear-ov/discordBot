import disnake.ext.commands.errors
from disnake.ext import commands
import time
from Userform import User, EMBED_CLASS, SETTING
import asyncio
from datetime import datetime
ID_ROLE_JOIN = 1085988777077522534
EMBED = EMBED_CLASS()
TDICT = {}


async def del_ban_user(member, role, end, ban_id, type_):
    now = datetime.now()
    if now < end:
        time_del = (end - now).seconds
        print(time_del)
        await asyncio.sleep(time_del)
    user = User(member.id)
    if user.get_ban_id(type_) == ban_id:
        if role is not None:
            await member.remove_roles(role)
        user.sub_ban(ban_id)
        await member.guild.get_channel(SETTING['channel']).send(f"{member.mention} разбанен причина: истекло время")


async def run_del_ban_role(members):
    async with asyncio.TaskGroup() as tg:
        for member in members:
            user = User(member.id)
            for ban in user.get_bans():
                type_, ban_id, end = ban
                end = datetime.strptime(end, SETTING['FORMAT_DATE'])
                now = datetime.now()
                role = member.get_role(SETTING[type_])
                if end <= now:
                    user.sub_ban(ban_id)
                    if role is not None:
                        await member.remove_roles(role)
                        await member.guild.get_channel(SETTING['channel']).send(
                            f"{member.mention} разбанен причина: истекло время")
                    continue
                tg.create_task(del_ban_user(member, role, end, ban_id, type_))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged on as', self.bot.user)
        # await asyncio.sleep(10)
        guild = self.bot.get_guild(SETTING['GUILD_ID'])
        await run_del_ban_role(guild.members)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author == self.bot.user:
            return
        User(message.author.id).add_money(1)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # role = discord.utils.get(member.guild.roles, id=ID_ROLE)
        role = member.guild.get_role(ID_ROLE_JOIN)
        User(member.id)
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send("That command wasn't found! Sorry :(")
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(embed=EMBED.get_error_embed("Ошибка доступа"), ephemeral=True)
        if isinstance(error, disnake.ext.commands.errors.CommandInvokeError):
            await ctx.edit_original_message(embed=EMBED.get_error_embed(error), components=None)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        author = member.id
        if before.channel is None and after.channel is not None:
            t1 = time.time()
            TDICT[author] = t1
        elif before.channel is not None and after.channel is None and author in TDICT:
            t2 = time.time()
            User(author).add_money(int(t2 - TDICT[author]))
            del TDICT[author]

    @commands.Cog.listener()
    async def on_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send("That command wasn't found! Sorry :(")
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(embed=EMBED.get_error_embed("Ошибка доступа"), ephemeral=True)


def setup(bot):
    bot.add_cog(Events(bot))