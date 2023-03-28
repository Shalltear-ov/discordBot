from typing import Optional
from disnake.ext import commands
import disnake
import asyncio
from disnake import ButtonStyle, Emoji
from disnake.ui import Button
from Userform import User, EMBED_CLASS, SHOP_ROLE, Select

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

    @staticmethod
    async def get_role_shop_list(start, sort='count', reverse='DESC'):
        ln = SHOP.len()
        if abs(start) >= ln:
            start = 0
        if start < 0:
            start = ln - (ln + start)
        roles = tuple(SHOP.get_role_shop(start, sort, reverse))
        select = Select().get_shop_sort_select(sort, reverse, EMOJI_SORT)
        components = [[], [select], []]
        for num, role in roles:
            btn = Button(style=ButtonStyle.green, label=f"{num}", custom_id=f'buy {role[0]} {role[2]}', row=1)
            components[0].append(btn)
        components[2].append(
            Button(style=ButtonStyle.green, label=f"Назад", custom_id=f'shop {start - 4} {sort} {reverse}', row=2))
        components[2].append(
            Button(style=ButtonStyle.green, label=f"Вперед", custom_id=f'shop {start + 4} {sort} {reverse}', row=2))
        embed = EMBED.get_shop_embed(roles)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/882429179512123463/1b2e01e540d1451e4699615f0a885f7e"
                                ".png?size=1024")
        return embed, components

    @commands.slash_command(name='shop', description='role shop', guild_ids=[GUILD_ID])
    async def shop(self, ctx: disnake.MessageCommandInteraction):
        global EMOJI_SORT
        EMOJI_SORT = self.bot.get_emoji(1089948016003272714)
        embed, components = await self.get_role_shop_list(0)
        await ctx.send(embed=embed, components=components)
        try:
            tasks = [asyncio.create_task(
                self.bot.wait_for(event="button_click", check=lambda message: message.author == ctx.author
                                  and message.component.custom_id.startswith(('shop', 'open', 'buy'))),
                name="button_click"),
                asyncio.create_task(
                    self.bot.wait_for(event="dropdown", check=lambda message: message.author == ctx.author
                                      and message.component.custom_id.startswith('sort')),
                    name="dropdown")]
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=30)
            print(done)
            if done:
                event, call_back = list(done)[0].get_name(), list(done)[0].result()
                for task in tasks:
                    task.cancel()
                if event == "dropdown":
                    await self.dropdown_member(call_back)
                elif event == "button_click":
                    await self.button_click_member(call_back)
            else:
                raise asyncio.TimeoutError
        except asyncio.TimeoutError:
            for component in components:
                for button in component:
                    button.disabled = True
            await ctx.edit_original_message(components=components)
            return

    # @commands.Cog.listener("on_button_click")
    async def button_click_member(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id.startswith('shop'):
            start, sort, reverse = inter.component.custom_id.split()[1:]
            embed, components = await self.get_role_shop_list(int(start), sort, reverse)
            await inter.response.edit_message(embed=embed, components=components)
            try:
                tasks = [asyncio.create_task(
                    self.bot.wait_for(event="button_click", check=lambda message: message.author == inter.author
                                      and message.component.custom_id.startswith(('shop', 'open', 'buy'))),
                    name="button_click"),
                    asyncio.create_task(
                        self.bot.wait_for(event="dropdown", check=lambda message: message.author == inter.author
                                          and message.component.custom_id.startswith('sort')),
                        name="dropdown")]
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=30)
                if done:
                    event, call_back = list(done)[0].get_name(), list(done)[0].result()
                    for task in tasks:
                        task.cancel()
                    if event == "dropdown":
                        await self.dropdown_member(call_back)
                    elif event == "button_click":
                        await self.button_click_member(call_back)
                else:
                    raise asyncio.TimeoutError
            except asyncio.TimeoutError:
                for component in components:
                    for button in component:
                        button.disabled = True
                await inter.edit_original_message(components=components)
                return
        elif inter.component.custom_id.startswith('buy'):
            _, role_id, cost = inter.component.custom_id.split()
            embed = EMBED.get_buy_embed(inter.author.id, role_id, int(cost))
            components = [
                Button(style=ButtonStyle.green, label=f"Подтвердить", custom_id=f'accept buy {role_id}', row=1),
                Button(style=ButtonStyle.green, label=f"Отклонить", custom_id=f'dont buy', row=1)
            ]
            await inter.response.edit_message(embed=embed, components=components)
            try:
                mes = await self.bot.wait_for(
                    event="button_click", timeout=5, check=lambda message: message.author == inter.author
                    and message.component.custom_id.startswith(('accept', 'dont buy')))
                await self.button_click_member(mes)
            except asyncio.TimeoutError:
                for button in components:
                    button.disabled = True
                await inter.edit_original_message(components=components)
                return

        elif inter.component.custom_id == 'dont buy':
            embed, components = await self.get_role_shop_list(0)
            await inter.response.edit_message(embed=embed, components=components)
            try:
                tasks = [asyncio.create_task(
                    self.bot.wait_for(event="button_click", check=lambda message: message.author == inter.author
                                      and message.component.custom_id.startswith(('shop', 'open', 'buy'))),
                    name="button_click"),
                    asyncio.create_task(
                        self.bot.wait_for(event="dropdown", check=lambda message: message.author == inter.author
                                          and message.component.custom_id.startswith('sort')),
                        name="dropdown")]
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=30)
                if done:
                    event, call_back = list(done)[0].get_name(), list(done)[0].result()
                    for task in tasks:
                        task.cancel()
                    if event == "dropdown":
                        await self.dropdown_member(call_back)
                    elif event == "button_click":
                        await self.button_click_member(call_back)
                else:
                    raise asyncio.TimeoutError
            except asyncio.TimeoutError:
                for component in components:
                    for button in component:
                        button.disabled = True
                await inter.edit_original_message(components=components)
                return
        elif inter.component.custom_id.startswith('accept buy'):
            role_id = inter.component.custom_id.split()[2]
            key = SHOP.buy_role(role_id, User(inter.author.id))
            if key:
                role = inter.guild.get_role(int(role_id))
                if role is not None:
                    await inter.author.add_roles(role)
                    await inter.response.edit_message("ty", embed=None, components=None)
            else:
                await inter.response.edit_message("Не хватает монет", embed=None, components=None)

    async def dropdown_member(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "sort shop":
            start, sort, reverse = inter.values[0].split()[1:]
            embed, components = await self.get_role_shop_list(int(start), sort, reverse)
            await inter.response.edit_message(embed=embed, components=components)
            try:
                tasks = [asyncio.create_task(
                    self.bot.wait_for(event="button_click", check=lambda message: message.author == inter.author
                                      and message.component.custom_id.startswith(('shop', 'open', 'buy'))),
                    name="button_click"),
                    asyncio.create_task(
                        self.bot.wait_for(event="dropdown", check=lambda message: message.author == inter.author
                                          and message.component.custom_id.startswith('sort')),
                        name="dropdown")]
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=30)
                if done:
                    event, call_back = list(done)[0].get_name(), list(done)[0].result()
                    for task in tasks:
                        task.cancel()
                    if event == "dropdown":
                        await self.dropdown_member(call_back)
                    elif event == "button_click":
                        await self.button_click_member(call_back)
                else:
                    raise asyncio.TimeoutError
            except asyncio.TimeoutError:
                for component in components:
                    for button in component:
                        button.disabled = True
                await inter.edit_original_message(components=components)
                return


def setup(bot):
    bot.add_cog(Member(bot))
