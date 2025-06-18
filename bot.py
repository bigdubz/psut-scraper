from discord.ext import commands
from discord.ext.commands import Context
from variables import TOKEN

import main
import discord
import traceback
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)
_quit = False


@bot.event
async def on_ready():
    print("started")
    await main.login()
    await asyncio.sleep(1)
    await main.nav_to_stud_reg()
    await asyncio.sleep(1)

    try:
        print("Ready")
        await update()

    except Exception:
        print(traceback.format_exc())

        # Keep trying
        await update()
    
    finally:
        main.driver.quit()
        print("quit successful")

@bot.event
async def update():

    while True:
        print("looping")
        subjects = await main.load_data()
        updates = await main.write_data(subjects)
        # if "x" in updates, await (await bot.fetch_user(ID)).send(updates)
                
        await asyncio.sleep(5)

if __name__ == "__main__":
    bot.run(TOKEN)