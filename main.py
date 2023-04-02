import disnake
from config import SETTING
from disnake.ext import commands
import os
from typing import Optional

client = commands.Bot(command_prefix='!', intents=disnake.Intents.all())
client.remove_command('help')
cogs_list = []


@client.slash_command(name='load', description='load cogs')
@commands.has_permissions(administrator=True)
async def load(ctx: disnake.ApplicationCommandInteraction, extension):
    await ctx.send("wait...", ephemeral=True)
    client.load_extension(f"cogs.{extension}")
    await ctx.edit_original_message("Cogs is loaded")


@load.autocomplete("extension")
async def autocomplete(self, string: str):
    string = string.lower()
    return [cog for cog in cogs_list if string in cog.lower()]


@client.slash_command(name='unload', description='unload cogs')
@commands.has_permissions(administrator=True)
async def load(ctx: disnake.ApplicationCommandInteraction, extension):
    await ctx.send("wait...", ephemeral=True)
    client.unload_extension(f"cogs.{extension}")
    await ctx.edit_original_message("Cogs is unloaded")


@load.autocomplete("extension")
async def autocomplete(self, string: str):
    string = string.lower()
    return [cog for cog in cogs_list if string in cog.lower()]


@client.slash_command(name='reload', description='reload cogs')
@commands.has_permissions(administrator=True)
async def load(ctx: disnake.ApplicationCommandInteraction, extension):
    await ctx.send("wait...", ephemeral=True)
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.edit_original_message("Cogs is reloaded")


@load.autocomplete("extension")
async def autocomplete(self, string: str):
    string = string.lower()
    return [cog for cog in cogs_list if string in cog.lower()]


@client.slash_command(name='reload_all', description='reload cogs')
@commands.has_permissions(administrator=True)
async def load_all(ctx: disnake.ApplicationCommandInteraction):
    await ctx.send("wait...", ephemeral=True)
    for cog in cogs_list:
        client.unload_extension(f"cogs.{cog}")
        client.load_extension(f"cogs.{cog}")
    await ctx.edit_original_message("Cogs is reloaded")


for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        cogs_list.append(file[:-3])
        client.load_extension(f"cogs.{file[:-3]}")

if __name__ == '__main__':
    client.run(SETTING['token'])
