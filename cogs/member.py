from typing import Optional
from disnake.ext import commands
import disnake
import asyncio
from disnake import ButtonStyle, Emoji
from disnake.ui import Button
from Userform import User, EMBED_CLASS, SHOP_ROLE, Select
from View import SHOP as SHOP_VIEW
GUILD_ID = 972208613663854593
EMBED = EMBED_CLASS()
SHOP = SHOP_ROLE()
EMOJI_SORT = None


def pprint(obj):
    print(obj)
    return True


class Member(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(name='balance', description='get your balance', guild_ids=[GUILD_ID])
    async def balance(self, ctx, name: Optional[disnake.Member] = None):
        # await ctx.send(" dfd")
        if name is None:
            user_id = ctx.user.id
            image = ctx.user.avatar
            username = f'{ctx.user.name}#{ctx.user.discriminator}'
        else:
            user_id = name.id
            image = name.avatar
            username = f'{name.name}#{name.discriminator}'
        user = User(user_id)
        embed = EMBED.get_balance_embed(username, image, user.balance)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(name='shop', description='role shop', guild_ids=[GUILD_ID])
    async def shop(self, ctx: disnake.MessageCommandInteraction):
        view = SHOP_VIEW(ctx.author)
        embed = await view.shop_open(0)
        await ctx.response.send_message(embed=embed, view=view)
        await view.wait()
        await view.close()
        await ctx.edit_original_message(view=view)


def setup(bot):
    bot.add_cog(Member(bot))
