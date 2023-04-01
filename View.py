import disnake
from disnake.ui import View, Button, Modal, TextInput
from disnake import ButtonStyle
from Userform import SHOP_ROLE, Select, EMBED_CLASS, User
from config import SETTING
import asyncio
import requests
import random
from random import randint
from functools import partial
SHOP_DATA = SHOP_ROLE()
EMBED = EMBED_CLASS()


class VersusGame(View):
    def __init__(self, author, member, bet):
        super().__init__(timeout=10)
        self.author = author
        self.member = member
        self.bet = bet

    async def open_versus(self):
        accept_btn = Button(style=ButtonStyle.green, label="Accept", custom_id="accept_fight")
        accept_btn.callback = self.accept
        deny_btn = Button(style=ButtonStyle.red, label="Deny", custom_id="deny_fight")
        deny_btn.callback = self.delete
        self.add_item(accept_btn)
        self.add_item(deny_btn)
        return self

    async def accept(self, inter: disnake.MessageInteraction):
        if inter.author != self.member and self.member is not None:
            return
        if inter.author == self.author:
            return
        if User(inter.author.id).balance < abs(self.bet):
            await inter.response.send_message(content="This user didn't have this amount of coins on balance.",
                                            ephemeral=True)
            return
        self.stop()
        self.clear_items()
        self.member = inter.author
        embed = EMBED.wait_result_versus_embed("https://media2.giphy.com/media/mMDEmlkm6XQKv0zgjG/giphy.gif?cid=ecf05e4754gmv06hxarhkbz152jf8p6xto4eif1gb0p7zc83&rid=giphy.gif")
        await inter.response.edit_message(embed=embed, view=self)
        await asyncio.sleep(4.05)
        winner = [self.author, self.member][randint(0, 1)]
        if winner.id == self.author.id:
            User(self.member.id).remove_money(self.bet)
        else:
            User(self.author.id).remove_money(self.bet)
        User(winner.id).add_money(self.bet)
        await inter.edit_original_message(f"Победитель {winner.mention}", embed=None, view=None)

    async def delete(self, inter: disnake.MessageInteraction):
        if inter.author != self.author:
            return
        self.stop()
        embed = EMBED.wait_result_versus_embed(VersusGame.get_giphy_gif("count to 5"))
        await inter.message.delete()
        # print(help(inter))
        # self.stop()
        # await inter.response.edit_message("fff")

    async def close(self):
        for item in self.children:
            item.disabled = True
        return self

    @staticmethod
    def get_giphy_gif(item_key):
        api_endpoint = "http://api.giphy.com/v1/gifs/search"

        api_key = SETTING['giphy_api_token']

        params = {
            "api_key": api_key,
            "q": item_key,
            "limit": 10,  # Maximum number of results to return
        }
        response = requests.get(api_endpoint, params=params)
        gifs = response.json()["data"]
        random_gif = random.choice(gifs)
        gif_url = random_gif["images"]["original"]["url"]
        return gif_url


class Git_away(View):
    def __init__(self):
        super().__init__(timeout=5)
        btn = Button(style=ButtonStyle.green, label=f"Получить 100 монет", row=1, custom_id='None')
        btn.callback = self.click
        self.add_item(btn)

    async def click(self, inter: disnake.MessageInteraction):
        self.stop()
        self.clear_items()
        embed = EMBED.win_git_embed(inter.author)
        await inter.response.edit_message(embed=embed, view=self)
        User(inter.author.id).add_money(100)

    async def close(self):
        for item in self.children:
            item.disabled = True
        return self


class SHOP(View):
    def __init__(self, author):
        super().__init__(timeout=10)
        self.author = author

    async def accept(self, inter: disnake.MessageInteraction):
        if self.author != inter.author:
            return
        self.clear_items()
        role_id = inter.component.custom_id.split()[2]
        key = SHOP_DATA.buy_role(role_id, User(inter.author.id))
        if key:
            role = inter.guild.get_role(int(role_id))
            if role is not None:
                User(inter.author.id).add_item('role', int(role_id))
                await inter.response.edit_message("ty", embed=None, view=self)
        else:
            await inter.response.edit_message("Не хватает монет", embed=None, view=self)
        self.stop()

    async def discard(self, inter: disnake.MessageInteraction):
        if self.author != inter.author:
            return
        self.clear_items()
        embed = await self.shop_open(0)
        await inter.response.edit_message(embed=embed, view=self)

    async def buy(self, inter: disnake.MessageInteraction):
        if self.author != inter.author:
            return
        self.clear_items()
        _, role_id, cost = inter.component.custom_id.split()
        embed = EMBED.get_buy_embed(inter.author.id, role_id, int(cost))
        btn1 = Button(style=ButtonStyle.green, label=f"Подтвердить", custom_id=f'accept buy {role_id}', row=1)
        btn1.callback = self.accept
        self.add_item(btn1)
        btn2 = Button(style=ButtonStyle.green, label=f"Отклонить", custom_id=f'dont buy', row=1)
        btn2.callback = self.discard
        self.add_item(btn2)
        await inter.response.edit_message(embed=embed, view=self)

    async def shop_open(self, start, sort='count', reverse='DESC'):
        ln = SHOP_DATA.len()
        if abs(start) >= ln:
            start = 0
        if start < 0:
            start = ln - (ln + start)
        roles = tuple(SHOP_DATA.get_role_shop(start, sort, reverse))
        for num, role in roles:
            btn = Button(style=ButtonStyle.green, label=f"{num}", custom_id=f'buy {role[0]} {role[2]}', row=1)
            btn.callback = self.buy
            self.add_item(btn)
        select = Select().get_shop_sort_select(sort, reverse, None)
        select.callback = self.sort
        self.add_item(select)
        prev = Button(style=ButtonStyle.green, label=f"Назад", custom_id=f'shop {start - 4} {sort} {reverse}', row=3)
        next_ = Button(style=ButtonStyle.green, label=f"Вперед", custom_id=f'shop {start + 4} {sort} {reverse}', row=3)
        prev.callback = self.next_page
        next_.callback = self.next_page
        self.add_item(prev)
        self.add_item(next_)
        embed = EMBED.get_shop_embed(roles)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/882429179512123463/1b2e01e540d1451e4699615f0a885f7e"
                                ".png?size=1024")
        return embed

    async def next_page(self, inter: disnake.MessageInteraction):
        if self.author != inter.author:
            return
        self.clear_items()
        start, sort, reverse = inter.component.custom_id.split()[1:]
        embed = await self.shop_open(int(start), sort, reverse)
        await inter.response.edit_message(embed=embed, view=self)

    async def sort(self, inter: disnake.MessageInteraction):
        if self.author != inter.author:
            return
        self.clear_items()
        start, sort, reverse = inter.values[0].split()[1:]
        embed = await self.shop_open(int(start), sort, reverse)
        await inter.response.edit_message(embed=embed, view=self)

    async def close(self):
        for item in self.children:
            item.disabled = True
        return self


class ProfileView(View):
    def __init__(self, author, is_author):
        super().__init__(timeout=30)
        self.is_author = is_author
        self.author = author
        # self.dont_stop = False

    async def open_profile(self):
        self.clear_items()
        sot_set = Button(label="Соц сети", style=disnake.ButtonStyle.blurple)
        sot_set.callback = self.open_social_network
        self.add_item(sot_set)
        if self.is_author:
            invent = Button(label="Инвентарь", style=disnake.ButtonStyle.blurple, custom_id='0')
            invent.callback = self.next_page
            self.add_item(invent)
            status = Button(label="edit status", style=disnake.ButtonStyle.blurple)
            status.callback = self.edit_status
            self.add_item(status)

    async def invent_open(self, start=0):
        self.clear_items()
        user = User(self.author.id)
        ln = user.len_invents()
        if abs(start) >= ln:
            start = 0
        if start < 0:
            start = ln - (ln + start)
        items = tuple(user.get_items(start))
        embed = EMBED.get_invent_embed(items, self.author)
        for num, item in items:
            type_, value = item
            btn = Button(style=ButtonStyle.green, label=f"{num}", row=1)
            btn.callback = partial(self.open_item, type_, value)
            self.add_item(btn)
        prev = Button(style=ButtonStyle.green, label=f"Назад", custom_id=f'{start - 4}', row=2)
        next_ = Button(style=ButtonStyle.green, label=f"Вперед", custom_id=f'{start + 4}', row=2)
        prev.callback = self.next_page
        next_.callback = self.next_page
        self.add_item(prev)
        self.add_item(next_)
        prof = Button(label="К профилю", style=disnake.ButtonStyle.blurple, row=2)
        prof.callback = self.bck_profile
        self.add_item(prof)
        return embed

    async def activate_role(self, type_, value, interaction: disnake.MessageInteraction):
        if self.author != interaction.author:
            return
        value = int(value[3:-1])
        key = User(interaction.author.id).del_item(type_, value)
        if key is not None:
            role = interaction.guild.get_role(value)
            if role is not None:
                await interaction.author.add_roles(role, reason='Ban')
        embed = await self.invent_open(0)
        await interaction.response.edit_message(embed=embed, view=self)

    async def delete_item(self, type_, value, interaction: disnake.MessageInteraction):
        if self.author != interaction.author:
            return
        if type_ == 'role':
            value = int(value[3:-1])
        User(interaction.author.id).del_item(type_, value)
        embed = await self.invent_open(0)
        await interaction.response.edit_message(embed=embed, view=self)

    async def open_item(self, type_, value, interaction: disnake.MessageInteraction):
        if self.author != interaction.author:
            return
        self.clear_items()
        embed = EMBED.get_item_embed(type_, value)
        if type_ == 'role':
            activate = Button(style=ButtonStyle.green, label="Активировать", row=1)
            activate.callback = partial(self.activate_role, type_, value)
            self.add_item(activate)
        delete = Button(style=ButtonStyle.red, label="Удалить", row=1)
        delete.callback = partial(self.delete_item, type_, value)
        self.add_item(delete)
        back = Button(style=ButtonStyle.blurple, label="Назад", row=1)
        back.callback = self.back_invent
        self.add_item(back)
        await interaction.response.edit_message(embed=embed, view=self)

    async def back_invent(self, interaction: disnake.Interaction):
        if self.author != interaction.author:
            return
        self.clear_items()
        embed = await self.invent_open(0)
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: disnake.MessageInteraction):
        if self.author != interaction.author:
            return
        start = int(interaction.component.custom_id)
        embed = await self.invent_open(start)
        await interaction.response.edit_message(embed=embed, view=self)

    async def bck_profile(self, interaction: disnake.Interaction):
        if self.author != interaction.author:
            return
        self.clear_items()
        await self.open_profile()
        embed = EMBED.profile_embed(interaction.author)
        await interaction.response.edit_message(embed=embed, view=self)

    async def edit_status(self, interaction: disnake.Interaction):
        if self.author != interaction.author:
            return
        coins_count = TextInput(label="About me", placeholder="Write something about yourself.",
                                custom_id="desc", style=disnake.TextInputStyle.short, max_length=140)
        await interaction.response.send_modal(
            modal=Modal(title="Let's change it.", components=coins_count, custom_id='edit_desc'))

    async def open_social_network(self, interaction: disnake.Interaction):
        if self.author != interaction.author:
            return
        self.clear_items()
        embed, result = EMBED.social_network_embed(*User(interaction.author.id).get_social(), interaction.author)
        for soc, url in result.items():
            btn = Button(label=soc, style=disnake.ButtonStyle.url, row=1, url=url)
            self.add_item(btn)
        if self.is_author:
            edit_social = Button(label="Изменить соц сети", style=disnake.ButtonStyle.blurple, row=2)
            edit_social.callback = self.edit_social_modal
            self.add_item(edit_social)
        back = Button(label="Назад", style=disnake.ButtonStyle.blurple, row=2)
        back.callback = self.bck_profile
        self.add_item(back)
        await interaction.response.edit_message(embed=embed, view=self)

    async def edit_social_modal(self, interaction: disnake.Interaction):
        if self.author != interaction.author:
            return
        vk, instagram, telegram = User(interaction.author.id).get_social()
        vk_t = TextInput(label="ПРОФИЛЬ ВКОНТАКТЕ", placeholder="VK",
                         custom_id="vk", style=disnake.TextInputStyle.short, max_length=50, min_length=15, value=vk)
        inst_t = TextInput(label="ПРОФИЛЬ INSTAGRAM", placeholder="VK",
                           custom_id="inst", style=disnake.TextInputStyle.short, max_length=50, min_length=22,
                           value=instagram)
        tele_t = TextInput(label="АКАУНТ TELEGRAM", placeholder="VK",
                           custom_id="tele", style=disnake.TextInputStyle.short, max_length=50, min_length=13,
                           value=telegram)
        components = [vk_t, inst_t, tele_t]
        # self.dont_stop = True
        await interaction.response.send_modal(
            modal=Modal(title="Let's change it.", components=components, custom_id='social'))

    async def close(self):
        for item in self.children:
            item.disabled = True
        return self
