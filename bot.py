from discord.ext import commands
from variables import TOKEN

import discord
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

async def handleClient(reader, writer):
    data = await reader.read(100)
    msg = data.decode()

    await bot.myUser.send(f"📢 {msg}")

    writer.close()
    await writer.wait_closed()


async def startServer():
    server = await asyncio.start_server(handleClient, "127.0.0.1", 65432)
    async with server:
        print("listening")
        await server.serve_forever()



@bot.event
async def on_ready():
    me = 451301920364167179
    bot.myUser = await bot.fetch_user(me)
    await bot.myUser.send("test")
    bot.loop.create_task(startServer())


if __name__ == "__main__":
    if TOKEN is not None:
        bot.run(TOKEN)
