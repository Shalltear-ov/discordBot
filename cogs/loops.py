from disnake.ext import commands, tasks
import time
from Userform import User, EMBED_CLASS, SETTING


class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.check_ban.start()

    @tasks.loop(seconds=5)
    async def check_ban(self):
        guild = self.bot.get_guild(SETTING['GUILD_ID'])
        if guild is not None:
            channel = guild.get_channel(972208614251053088)
            for member in guild.members:
                ban_key = member.get_role(972485080431886437)
                if ban_key is None:
                    continue
                user = User(member.id)
                bans = user.check_bans()
                if 'ban' not in bans:
                    # if ban_key in member.roles:
                    await member.remove_roles(ban_key)
                    await channel.send(f"{member.mention} разбанен причина: истекло время")


def setup(bot):
    pass
    # bot.add_cog(Loops(bot))