import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional
from disnake import Embed, Colour
DATA_USER = 'C:/Users/damir/OneDrive/discord/USER.db'
DATA_USER_PROFILE = 'PROFILE'
BAN_USERS = 'BAN'
COLOR_EMBED = (43, 45, 49)
FORMAT_DATE = "%d.%m.%Y %H:%M"
SETTING = {'token': 'MTA4NTg5NTk3NzY2OTUwNTA0NA.GdL4J-.c9KQ001Ncds_W4J3kjANP6o8GeFFpxdHibcgAc',
           'FORMAT_DATE': "%d.%m.%Y %H:%M", "GUILD_ID": 972208613663854593,
           'ban': 972485080431886437, 'channel': 972208614251053088}


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

    def create(self):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {DATA_USER_PROFILE}("
                            f"user_id INTEGER, balance INTEGER DEFAULT 0, ban_id INTEGER DEFAULT '[]')")
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {BAN_USERS}("
                            f"ban_id INTEGER PRIMARY KEY, type TEXT, user_id INTEGER, reason TEXT, end TEXT, "
                            f"moder_id TEXT)")
        self.connect.commit()

    def add_money(self, value: int):
        self.cursor.execute(f"UPDATE {DATA_USER_PROFILE} SET balance = (?) WHERE user_id = (?)",
                            [self.balance + value, self.user_id])
        self.connect.commit()
        self.balance += value

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
