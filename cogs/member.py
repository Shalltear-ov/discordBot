from typing import Optional
from disnake.ext import commands
import disnake
import asyncio
from disnake import ButtonStyle, Emoji
from disnake.ui import Button

from Userform import User, EMBED_CLASS, SHOP_ROLE, Select
from View import SHOP as SHOP_VIEW, ProfileView, VersusGame, Report_for_moder
from config import SETTING
from typing import Optional
EMBED = EMBED_CLASS()
SHOP = SHOP_ROLE()
EMOJI_SORT = None


def pprint(obj):
    print(obj)
    return True


class Member(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(name='balance', description='get your balance', guild_ids=[SETTING['GUILD_ID']])
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

    @commands.slash_command(name='shop', description='role shop', guild_ids=[SETTING['GUILD_ID']])
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
        user = member if member is not None else ctx.author
        view = ProfileView(ctx.author, member is None, user)
        await view.open_profile()
        if member is None:
            await ctx.send(embed=EMBED.profile_embed(ctx.author), view=view)
        else:
            await ctx.send(embed=EMBED.profile_embed(member), view=view)
        await view.wait()
        await view.close()
        await ctx.edit_original_message(view=view)

    @commands.Cog.listener("on_modal_submit")
    async def modal_status_edit(self, modal: disnake.ModalInteraction):
        values = modal.text_values
        if modal.custom_id == "edit_desc":
            user = User(modal.author.id)
            user.edit_desc(values['desc'])
            view = ProfileView(modal.author, True, modal.author)
            await view.open_profile()
            await modal.response.edit_message(embed=EMBED.profile_embed(modal.author), view=view)
        if modal.custom_id == "social":
            vk, instagram, telegram = values.values()
            vk = vk if vk.startswith("https://vk.com/") else "https://vk.com/"
            instagram = instagram if instagram.startswith("https://instagram.com/") else "https://instagram.com/"
            telegram = telegram if telegram.startswith("https://t.me/") else "https://t.me/"
            User(modal.author.id).edit_social(vk, instagram, telegram)
            view = ProfileView(modal.author, True, modal.author)
            await view.open_profile()
            await modal.response.edit_message(embed=EMBED.profile_embed(modal.author), view=view)

    @commands.slash_command(name="versus", description="Let you play with specific user for any bet.",
                            guild_ids=[SETTING['GUILD_ID']])
    async def versus(self, ctx: disnake.MessageCommandInteraction, bet: Optional[int], member: Optional[disnake.Member] = None):
        if User(ctx.author.id).balance < abs(bet):
            await ctx.response.send_message(content="Not enough coins on balance.", ephemeral=True)
            return
        if member is not None:
            if User(member.id).balance < abs(bet):
                await ctx.response.send_message(content="This user didn't have this amount of coins on balance.", ephemeral=True)
                return
        elif ctx.author == member:
            await ctx.response.send_message(content="No, ")
            return
        bet = abs(bet)
        view = VersusGame(ctx.author, member, bet)
        await view.open_versus()
        if member is not None:
            await ctx.response.send_message(content=f"{member.mention}", embed=EMBED.versus_embed(ctx.author, bet, view.get_giphy_gif("versus fight")), view=view)
        else:
            await ctx.response.send_message(embed=EMBED.versus_embed(ctx.author, bet, view.get_giphy_gif("versus fight")), view=view)
        await view.wait()
        await view.close()
        await ctx.edit_original_message(view=view)

    @commands.slash_command(name="report", description="Let you play with specific user for any bet.",
                            guild_ids=[SETTING['GUILD_ID']])
    async def report(self, ctx: disnake.MessageCommandInteraction, member: Optional[disnake.Member], reason):
        channel = self.bot.get_channel(972208614251053087)
        view = Report_for_moder(ctx.author, member, reason)
        await ctx.send("жалоба отправлена")
        await channel.send(f"> поступила жалоба от {ctx.author.mention} на {member.mention} по причине {reason}", view=view)


def setup(bot):
    bot.add_cog(Member(bot))
