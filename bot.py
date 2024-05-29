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
    shishi_id = 1198930964194283521
    me_id = 451301920364167179
    alaa_id = 300666842203160577
    me_user = await bot.fetch_user(me_id)
    shishi_user = await bot.fetch_user(shishi_id)
    alaa_user = await bot.fetch_user(alaa_id)

    while True:
        subjects = await main.load_data()
        updates = await main.write_data(subjects)
        if updates != '':
            if "Technical Writing" in updates or "Statistical Methods" in updates:
                await me_user.send(updates)
                await shishi_user.send(updates)

            await alaa_user.send(updates)


@bot.command(name="quit", description="Turns off the bot")
async def quit(ctx: Context):
    # not working for now
    return

    if not await bot.is_owner(ctx.message.author):
        await ctx.send("unauthorized")
        return
    
    _quit = True
    print("quit set to True")

if __name__ == "__main__":
    bot.run(TOKEN)