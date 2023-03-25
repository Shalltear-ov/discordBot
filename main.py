import disnake

from Userform import SETTING
from disnake.ext import commands
import os


client = commands.Bot(command_prefix='!', intents=disnake.Intents.all())
client.remove_command('help')


@client.slash_command(name='load', description='load cogs')
@commands.has_permissions(administrator=True)
async def load(ctx: disnake.ApplicationCommandInteraction, extension):
    await ctx.send("wait...", ephemeral=True)
    client.load_extension(f"cogs.{extension}")
    await ctx.edit_original_message("Cogs is loaded")


@client.slash_command(name='unload', description='unload cogs')
@commands.has_permissions(administrator=True)
async def load(ctx: disnake.ApplicationCommandInteraction, extension):
    await ctx.send("wait...", ephemeral=True)
    client.unload_extension(f"cogs.{extension}")
    await ctx.edit_original_message("Cogs is unloaded")


@client.slash_command(name='reload', description='reload cogs')
@commands.has_permissions(administrator=True)
async def load(ctx: disnake.ApplicationCommandInteraction, extension):
    await ctx.send("wait...", ephemeral=True)
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.edit_original_message("Cogs is reloaded")


for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        print(1)
        client.load_extension(f"cogs.{file[:-3]}")


if __name__ == '__main__':
    client.run(SETTING['token'])