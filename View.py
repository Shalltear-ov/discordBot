import disnake
from disnake.ui import View, Button, button, StringSelect, Modal, TextInput
from disnake import ButtonStyle
from Userform import SHOP_ROLE, Select, EMBED_CLASS, User

SHOP_DATA = SHOP_ROLE()
EMBED = EMBED_CLASS()


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
                await inter.author.add_roles(role)
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
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author

    @button(label="Edit bio.", style=disnake.ButtonStyle.blurple)
    async def edit(self, hui, interaction: disnake.Interaction):
        if self.author != interaction.author:
            return
        coins_count = TextInput(label="About me", placeholder="Write something about yourself.",
                                custom_id="desc", style=disnake.TextInputStyle.short, max_length=140)
        await interaction.response.send_modal(
            modal=Modal(title="Let's change it.", components=coins_count, custom_id='edit_desc'))
