from typing import Optional
from disnake.ext import commands
import disnake
import asyncio
from disnake import ButtonStyle, Emoji
from disnake.ui import Button
from Userform import User, EMBED_CLASS, SHOP_ROLE, Select, SETTING
from View import SHOP as SHOP_VIEW, ProfileView
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

    @commands.slash_command(name="profile", description="Let you see an information about specific user.",
                            guild_ids=[SETTING['GUILD_ID']])
    async def profile(self, ctx, member: Optional[disnake.Member] = None):
        view = ProfileView(ctx.author)
        if member is None:
            await ctx.send(embed=EMBED.profile_embed(ctx.author), view=view)
        else:
            await ctx.send(embed=EMBED.profile_embed(member), view=view)

    @commands.Cog.listener("on_modal_submit")
    async def modal_admin(self, modal: disnake.ModalInteraction):
        values = modal.text_values
        if modal.custom_id == "edit_desc":
            user = User(modal.author.id)
            user.edit_desc(values['desc'])
            await modal.response.edit_message(embed=EMBED.profile_embed(modal.author), view=ProfileView(modal.author))


def setup(bot):
    bot.add_cog(Member(bot))
