import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import json

load_dotenv()

TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print('Ready')

if __name__ == "__main__":
    bot.run(TOKEN)