from typing import Optional
from datetime import datetime, timedelta
from disnake.ext import commands
import disnake
import asyncio
from disnake.ui import View, Button, UserSelect, Modal, TextInput
from disnake import ButtonStyle, TextInputStyle
from Userform import User, EMBED_CLASS, SETTING

EMBED = EMBED_CLASS()


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(name='admin', description='admin panel', guild_ids=[SETTING['GUILD_ID']])
    @commands.has_permissions(administrator=True)
    async def admin_panel(self, ctx):
        select_components = [[
            Button(style=ButtonStyle.green, label="add money", custom_id='add money'),
            Button(style=ButtonStyle.red, label="reset money", custom_id='reset money'),
            Button(style=ButtonStyle.red, label="ban", custom_id='ban admin'),
            Button(style=ButtonStyle.green, label="unban", custom_id='unban admin')
        ]]
        await ctx.send("Открыта админ панель", ephemeral=True, components=select_components)
        try:
            await self.bot.wait_for(
                "button_click", timeout=30, check=lambda message: message.author == ctx.author)
        except asyncio.TimeoutError:
            for component in select_components:
                for button in component:
                    button.disabled = True
            await ctx.edit_original_message(components=select_components)
            return

    @commands.Cog.listener("on_button_click")
    async def button_click_admin(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == 'add money':
            select_components = [[
                UserSelect(min_values=1, max_values=1, custom_id='add money user_list')
            ]]
            await inter.response.edit_message("Выберите пользователтя", components=select_components)
            try:
                await self.bot.wait_for(
                    "dropdown", timeout=30, check=lambda message: message.author == inter.author)
            except asyncio.TimeoutError:
                for component in select_components:
                    for button in component:
                        button.disabled = True
                await inter.edit_original_message(components=select_components)
                return
        elif inter.component.custom_id == 'reset money':
            select_components = [[
                UserSelect(min_values=1, max_values=1, custom_id='reset money user_list')
            ]]
            await inter.response.edit_message("Выберите пользователтя", components=select_components)
            try:
                await self.bot.wait_for(
                    "dropdown", timeout=20, check=lambda message: message.author == inter.author)
            except asyncio.TimeoutError:
                for component in select_components:
                    for button in component:
                        button.disabled = True
                await inter.edit_original_message(components=select_components)
                return
        elif inter.component.custom_id == 'ban admin':
            select_components = [[
                UserSelect(min_values=1, max_values=1, custom_id='ban admin user_list')
            ]]
            await inter.response.edit_message("Выберите пользователтя", components=select_components)
            try:
                await self.bot.wait_for(
                    "dropdown", timeout=30, check=lambda message: message.author == inter.author)
            except asyncio.TimeoutError:
                for component in select_components:
                    for button in component:
                        button.disabled = True
                await inter.edit_original_message(components=select_components)
                return

        elif inter.component.custom_id == 'unban admin':
            select_components = [[
                UserSelect(min_values=1, max_values=1, custom_id='unban admin user_list')
            ]]
            await inter.response.edit_message("Выберите пользователтя", components=select_components)
            try:
                await self.bot.wait_for(
                    "dropdown", timeout=30, check=lambda message: message.author == inter.author)
            except asyncio.TimeoutError:
                for component in select_components:
                    for button in component:
                        button.disabled = True
                await inter.edit_original_message(components=select_components)
                return

    @commands.Cog.listener("on_dropdown")
    async def dropdown_admin(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "add money user_list":
            user_id = inter.values[0]
            user_id_text_input = TextInput(label="ID user", placeholder=None,
                                           custom_id="id", style=TextInputStyle.short, max_length=50, value=user_id)
            coins_count = TextInput(label="Coins", placeholder="Count",
                                    custom_id="count", style=TextInputStyle.short, max_length=50)

            select_components = [user_id_text_input, coins_count]
            await inter.response.send_modal(modal=Modal(components=select_components,
                                                        title="add money", custom_id='add money result'))
        elif inter.component.custom_id == "reset money user_list":
            user_id = int(inter.values[0])
            user = User(user_id)
            user.reset_money()
            member = await inter.bot.fetch_user(user_id)
            await inter.response.edit_message('Бот успешно выполнил команду и отдыхает', view=None)
            await member.send("> Ваш баланс на сервере по какой-то причине был обнулен")
            await inter.followup.send(
                f'<@{inter.author.id}> успешно обнулил баланс <@{member.id}>', allowed_mentions=False)
        elif inter.component.custom_id == "ban admin user_list":
            user_id = inter.values[0]
            user_id_text_input = TextInput(label="ID user", placeholder=None,
                                           custom_id="id", style=TextInputStyle.short, max_length=50, value=user_id)
            time_count = TextInput(label="Time", placeholder="Count",
                                   custom_id="time", style=TextInputStyle.short, max_length=50)
            reason = TextInput(label="Reason", placeholder=None,
                               custom_id="reason", style=TextInputStyle.paragraph, max_length=50,
                               value="Администратор так решил")
            select_components = [user_id_text_input, reason, time_count]
            await inter.response.send_modal(modal=Modal(components=select_components,
                                                        title="BAN", custom_id='ban admin result'))

        elif inter.component.custom_id == "unban admin user_list":
            user_id = int(inter.values[0])
            user = User(user_id)
            key = user.unban('ban')
            if key:
                member = inter.guild.get_member(user_id)
                role = inter.guild.get_role(972485080431886437)
                await member.remove_roles(role)
                await inter.response.edit_message('Бот успешно выполнил команду и отдыхает', view=None)
                await member.send("> Вы были разбаненены")
                await inter.followup.send(
                    f'<@{inter.author.id}> успешно разбанил <@{member.id}>', allowed_mentions=False)
            else:
                await inter.response.edit_message('Бан отсутствует', view=None)

    @commands.Cog.listener("on_modal_submit")
    async def modal_admin(self, modal: disnake.ModalInteraction):
        values = modal.text_values
        if modal.custom_id == "add money result":
            if not values['count'].isdigit() or not values['id'].isdigit():
                raise ValueError("данные не коректны")
            user_id, count = int(values['id']), int(values['count'])
            member = await modal.bot.fetch_user(user_id)
            User(user_id).add_money(count)
            await member.send(embed=EMBED.add_money_embed(count))
            await modal.response.edit_message("Бот успешно выполнил команду и отдыхает", view=None)
            await modal.send(
                f'<@{modal.author.id}> успешно предал <@{member.id}> {values["count"]} <a:Coin'
                f':1085923871238135911>')
        if modal.custom_id == "ban admin result":
            if not values['id'].isdigit() or not values['time'].isdigit():
                raise ValueError("данные не коректны")
            user_id, time = int(values['id']), int(values['time'])
            member = modal.guild.get_member(user_id)
            user = User(user_id)
            end = (datetime.now() + timedelta(seconds=time * 60)).strftime(SETTING['FORMAT_DATE'])
            ban_id = user.ban('ban', values['reason'], end, modal.author.id)
            role = modal.guild.get_role(972485080431886437)
            await member.add_roles(role, reason='Ban')
            await member.send(embed=EMBED.ban_user_embed(values['reason'], modal.author, end))
            await modal.response.edit_message("Бот успешно выполнил команду и отдыхает", view=None)
            await modal.send(
                f'<@{modal.author.id}> успешно забанил <@{member.id}> причина: {values["reason"]}')
            await asyncio.sleep(time * 60)
            await member.remove_roles(role)
            user.unban(ban_id)
            await modal.send(f"{member.mention} разбанен причина: истекло время")


def setup(bot):
    bot.add_cog(Admin(bot))
