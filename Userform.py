import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional

import disnake
from disnake import Embed, Colour, SelectOption
from disnake.ui import StringSelect

DATA_USER = 'USER.db'
DATA_USER_PROFILE = 'PROFILE'
DATA_USER_SOCIAL = "SOCIAL"
DATA_USER_SHOP = 'SHOP'
BAN_USERS = 'BAN'
COLOR_EMBED = (43, 45, 49)
FORMAT_DATE = "%d.%m.%Y %H:%M"


class User:
    def __init__(self, user_id):
        self.connect = sqlite3.connect(DATA_USER)
        self.cursor = self.connect.cursor()
        self.user_id = user_id
        self.cursor.execute(f"SELECT balance FROM {DATA_USER_PROFILE} WHERE user_id = {user_id}")
        data = self.cursor.fetchone()
        if data is None:
            self.cursor.execute(f"INSERT INTO {DATA_USER_PROFILE} (user_id) VALUES(?)", [user_id])
            self.connect.commit()
            self.balance = 0
        else:
            self.balance = data[0]
        self.cursor.execute(f"SELECT desc FROM {DATA_USER_PROFILE} WHERE user_id = {user_id}")
        data = self.cursor.fetchone()
        if data[0] is None:
            self.desc = "There is no bio yet."
        else:
            self.desc = data[0]

    def create(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {BAN_USERS}("
                            f"ban_id INTEGER PRIMARY KEY, type TEXT, user_id INTEGER, reason TEXT, end TEXT, "
                            f"moder_id TEXT)")
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATA_USER_PROFILE}("
                            f"user_id INTEGER, balance INTEGER DEFAULT 0, desc STR, ban_id INTEGER DEFAULT '[]')")
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATA_USER_SOCIAL}("
                            f"user_id INTEGER, Vk TEXT DEFAULT 'https://vk.com/', Instagram TEXT DEFAULT "
                            f"'https://instagram.com/', Telegram TEXT DEFAULT 'https://t.me/')")
        self.connect.commit()

    def add_money(self, value: int):
        self.cursor.execute(f"UPDATE {DATA_USER_PROFILE} SET balance = (?) WHERE user_id = (?)",
                            [self.balance + value, self.user_id])
        self.connect.commit()
        self.balance += value

    def remove_money(self, value: int):
        if self.balance - value >= 0:
            self.cursor.execute(f"UPDATE {DATA_USER_PROFILE} SET balance = (?) WHERE user_id = (?)",
                                [self.balance - value, self.user_id])
            self.connect.commit()
            self.balance -= value
        else:
            self.reset_money()

    def reset_money(self):
        self.cursor.execute(f"UPDATE {DATA_USER_PROFILE} SET balance = (?) WHERE user_id = (?)",
                            [0, self.user_id])
        self.connect.commit()
        self.balance = 0

    def add_ban(self, ban_id):
        self.cursor.execute(f"SELECT ban_id FROM {DATA_USER_PROFILE} WHERE user_id = {self.user_id}")
        data = json.loads(self.cursor.fetchone()[0])
        data.append(ban_id)
        self.cursor.execute(f"UPDATE {DATA_USER_PROFILE} SET ban_id = (?) WHERE user_id = (?)",
                            [json.dumps(data), self.user_id])
        self.connect.commit()

    def sub_ban(self, ban_id):
        self.cursor.execute(f"SELECT ban_id FROM {DATA_USER_PROFILE} WHERE user_id = {self.user_id}")
        data = json.loads(self.cursor.fetchone()[0])
        if ban_id in data:
            del data[data.index(ban_id)]
        self.cursor.execute(f"UPDATE {DATA_USER_PROFILE} SET ban_id = (?) WHERE user_id = (?)",
                            [json.dumps(data), self.user_id])
        self.connect.commit()

    def ban_is_be(self, type_):
        self.cursor.execute(f"SELECT ban_id FROM {DATA_USER_PROFILE} WHERE user_id = {self.user_id}")
        data = json.loads(self.cursor.fetchone()[0])
        for ban_id in data:
            self.cursor.execute(f"SELECT type FROM {BAN_USERS} WHERE ban_id = {int(ban_id)}")
            data = self.cursor.fetchone()
            if data is None:
                continue
            if data[0] == type_:
                return True
        return False

    def check_bans(self):
        self.cursor.execute(f"SELECT ban_id FROM {DATA_USER_PROFILE} WHERE user_id = {self.user_id}")
        data = json.loads(self.cursor.fetchone()[0])
        result = []
        for ban_id in data:
            self.cursor.execute(f"SELECT type, ban_id, end FROM {BAN_USERS} WHERE ban_id = {int(ban_id)}")
            type_, ban_id, end = self.cursor.fetchone()
            if end is None:
                result.append(type_)
            elif datetime.strptime(end, FORMAT_DATE) <= datetime.now():
                self.sub_ban(ban_id)
            else:
                result.append(type_)
        return result

    def get_ban_id(self, type_):
        self.cursor.execute(f"SELECT ban_id FROM {DATA_USER_PROFILE} WHERE user_id = {self.user_id}")
        data = json.loads(self.cursor.fetchone()[0])
        for ban_id in data:
            self.cursor.execute(f"SELECT type, ban_id, end FROM {BAN_USERS} WHERE ban_id = {int(ban_id)}")
            type_ban, ban_id, end = self.cursor.fetchone()
            if type_ == type_ban:
                return ban_id
        return False

    def ban(self, type_: str, reason: str, end: str, moder_id: int):
        if self.ban_is_be(type_):
            self.sub_ban(self.get_ban_id(type_))
        self.cursor.execute(f"INSERT INTO {BAN_USERS} (type, user_id, reason, end, moder_id) VALUES(?,?,?,?,"
                            f"?) RETURNING ban_id",
                            [type_, self.user_id, reason, end, moder_id])
        data = self.cursor.fetchone()
        self.add_ban(data[0])
        self.connect.commit()
        return data[0]

    def get_bans(self):
        self.cursor.execute(f"SELECT ban_id FROM {DATA_USER_PROFILE} WHERE user_id = {self.user_id}")
        data = json.loads(self.cursor.fetchone()[0])
        result = []
        for ban_id in data:
            self.cursor.execute(f"SELECT type, ban_id, end FROM {BAN_USERS} WHERE ban_id = {int(ban_id)}")
            type_ban, ban_id, end = self.cursor.fetchone()
            result.append((type_ban, ban_id, end))
        return result

    def unban(self, type_):
        ban_id = self.get_ban_id(type_)
        if not ban_id:
            return False
        self.sub_ban(ban_id)
        return True

    def edit_desc(self, desc):
        self.cursor.execute(f"UPDATE {DATA_USER_PROFILE} SET desc = (?) WHERE user_id = (?)",
                            [desc, self.user_id])
        self.connect.commit()

    def get_social(self):
        self.cursor.execute(f"SELECT Vk, Instagram, Telegram FROM {DATA_USER_SOCIAL} WHERE user_id = {self.user_id}")
        data = self.cursor.fetchone()
        if data is None:
            self.cursor.execute(f"INSERT INTO {DATA_USER_SOCIAL} (user_id) VALUES(?)", [self.user_id])
            self.connect.commit()
            return ['https://vk.com/', 'https://instagram.com/', 'https://t.me/']
        else:
            return data

    def edit_social(self, vk, instagram, telegram):
        self.cursor.execute(f"UPDATE {DATA_USER_SOCIAL} SET Vk = (?), Instagram = (?), Telegram = (?) WHERE user_id = "
                            f"(?)",
                            [vk, instagram, telegram, self.user_id])
        self.connect.commit()


class SHOP_ROLE:
    def __init__(self):
        self.connect = sqlite3.connect(f'{DATA_USER_SHOP}.db')
        self.cursor = self.connect.cursor()

    def create(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATA_USER_SHOP}("
                            f"role_id INTEGER, user_id INTEGER, cost INTEGER, count INTEGER DEFAULT 0, date "
                            f"INTEGER PRIMARY KEY)")
        self.connect.commit()

    def get_role_shop(self, start, sort, reverse):
        self.cursor.execute(f"SELECT role_id, user_id, cost, count FROM {DATA_USER_SHOP} ORDER BY {sort} {reverse} "
                            f"LIMIT 4 OFFSET {start}")
        return enumerate(self.cursor.fetchall(), start=start + 1)

    def len(self):
        self.cursor.execute(f"SELECT COUNT(*) FROM {DATA_USER_SHOP}")
        ln = self.cursor.fetchone()[0]
        return ln

    def add_role_shop(self, role_id, user_id, cost):
        self.cursor.execute(f"SELECT role_id FROM {DATA_USER_SHOP} WHERE role_id = (?)", [role_id])
        if self.cursor.fetchone() is None:
            self.cursor.execute(f"INSERT INTO {DATA_USER_SHOP} (role_id, user_id, cost) VALUES(?,?,"
                                f"?)",
                                [role_id, user_id, cost])
            self.connect.commit()

    def buy_role(self, role_id, user: User):
        self.cursor.execute(f"SELECT cost, count FROM {DATA_USER_SHOP} WHERE role_id = (?)", [role_id])
        cost, count = self.cursor.fetchone()
        if cost <= user.balance:
            self.cursor.execute(f"UPDATE {DATA_USER_SHOP} SET count = (?) WHERE role_id = (?)",
                                [count + 1, role_id])
            self.connect.commit()
            user.add_money(-cost)
            return True
        else:
            return False


class EMBED_CLASS:
    @staticmethod
    def get_error_embed(err):
        embed = Embed(
            title="Ошибка",
            color=Colour.from_rgb(*COLOR_EMBED)
        )
        err = str(f"""```diff\n-{err}```""")
        embed.add_field(name="Тип ошибки", value=err, inline=False)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/972208614251053087/1085942522083291237/png'
                                '-clipart-arrow-computer-icons-cancel-blue-logo_1.png')
        return embed

    @staticmethod
    def get_balance_embed(username, image, balance):
        embed = Embed(
            title=f"Баланс — {username}",
            color=Colour.from_rgb(*COLOR_EMBED)
        )
        embed.set_thumbnail(url=image)
        embed.add_field(name="Монетки <a:Coin:1085923871238135911>", value=f"```{balance}```", inline=False)
        return embed

    @staticmethod
    def add_money_embed(count):
        embed = Embed(
            title="Пополнение",
            color=Colour.from_rgb(*COLOR_EMBED),
            description=f"Количество:\n```{count}```"
        )
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1085923871238135911.gif?size=128&quality=lossless')
        return embed

    @staticmethod
    def ban_user_embed(reason, moder, end):
        embed = Embed(
            title="БАН",
            color=Colour.from_rgb(*COLOR_EMBED)
        )
        embed.add_field(name='Причина', value=f"```{reason}```")
        embed.add_field(name='Дата оканчания', value=f"```{end}```")
        embed.set_author(
            name=moder,
            icon_url=moder.avatar
        )
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1021345497727909928.webp?size=128&quality'
                                '=lossless')
        return embed

    @staticmethod
    def get_shop_embed(roles):
        embed = Embed(
            title="Магазин личных ролей",
            color=Colour.from_rgb(*COLOR_EMBED)
        )
        for num, role in roles:
            role_id, user_id, cost, count = role
            embed.add_field(name=f"**{num}**",
                            value=f"Роль <@&{role_id}>\n**Продавец:** <@{user_id}>\n"
                                  f"**Цена:** {cost}\n**Куплена раз:** {count}", inline=False)
        return embed

    @staticmethod
    def get_buy_embed(user_id, role_id, cost):
        embed = Embed(
            title="Купить роль в магазине",
            description=f"<@{user_id}>, Вы уверены, что хотите купить роль <@&{role_id}> за {cost} ?",
            color=Colour.from_rgb(*COLOR_EMBED))
        return embed

    @staticmethod
    def profile_embed(member):
        user = User(member.id)

        embed = Embed(
            title=f"Profile — {member}",
            color=Colour.from_rgb(55, 57, 62)
        )
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name="> About me", value=f"```{user.desc}```", inline=False)
        embed.add_field(name="> Balance <a:Coin:1085923871238135911>", value=f"```{user.balance}    ```", inline=True)
        embed.add_field(name="> Time in voice chat", value="```undefined```", inline=True)

        return embed

    @staticmethod
    def social_network_embed(vk, instagram, telegram, member: disnake.Member):
        embed = Embed(
            title=f"Социальные сети — {member}")
        embed.set_thumbnail(member.avatar)
        result = dict()
        if len(vk) > len('https://vk.com/'):
            result['vk'] = vk
            embed.add_field(name='ВКонтакте', value=f"```{vk}```")
        else:
            embed.add_field(name='ВКонтакте', value="```Не установлен```")

        if len(instagram) > len("https://instagram.com/"):
            result['instagram'] = instagram
            embed.add_field(name="Instagram", value=f"```{instagram}```")
        else:
            embed.add_field(name='Instagram', value="```Не установлен```")

        if len(telegram) > len('https://t.me/'):
            result['telegram'] = telegram
            embed.add_field(name='Telegram', value=f"```{telegram}```")
        else:
            embed.add_field(name='Telegram', value="```Не установлен```")
        return embed, result

    @staticmethod
    def win_git_embed(member):
        embed = Embed(
            title=f"Победитель — {member}", description="получил 100 монет")

        return embed

    @staticmethod
    def versus_embed(first_member, cost, gif):
        embed = Embed(title=f"So what u gonna do, boi?\nAre you ready to bet your {cost} <a:Coin:1085923871238135911>?")
        embed.set_author(name=f"{first_member} invited you to a roll fight.", icon_url=f"{first_member.avatar}")
        embed.set_image(gif)
        return embed

    @staticmethod
    def wait_result_versus_embed(gif):
        embed = Embed(title=f"wait")
        embed.set_image(gif)

        return embed

    @staticmethod
    def error_permission_interaction(member):
        now = datetime.now()
        embed = Embed(title=f":x: Sorry, {member} but you can't use this.")
        embed.add_field(name="Wrong permissions", value="**This interaction belongs to another user.**")
        embed.add_field(name="", value=f"{now.strftime(FORMAT_DATE)}", inline=False)
        return embed

class Select:
    @staticmethod
    def get_shop_sort_select(sort, reverse, emoji=None):
        options = [
            SelectOption(
                label="Не популярные", description="Your favourite colour is red", emoji=emoji,
                value="shop 0 count ASC", default=sort == 'count' and reverse == 'ASC'
            ),
            SelectOption(
                label="Популярные", description="Your favourite colour is green", emoji=emoji,
                default=sort == 'count' and reverse == 'DESC', value="shop 0 count DESC"
            ),
            SelectOption(
                label="Старые", description="Your favourite colour is green", emoji=emoji,
                default=sort == 'date' and reverse == 'ASC', value="shop 0 date ASC"
            ),
            SelectOption(
                label="Новые", description="Your favourite colour is green", emoji=emoji,
                default=sort == 'date' and reverse == 'DESC', value="shop 0 date DESC"),
            SelectOption(
                label="Дешевые", description="Your favourite colour is green", emoji=emoji,
                default=sort == 'cost' and reverse == 'ASC', value="shop 0 cost ASC"
            ),
            SelectOption(
                label="Дорогие", description="Your favourite colour is green", emoji=emoji,
                default=sort == 'cost' and reverse == 'DESC', value="shop 0 cost DESC")
        ]

        return StringSelect(options=options, custom_id='sort shop', row=2)
