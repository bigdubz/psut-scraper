from discord.ext import commands
from variables import TOKEN

import main
import discord
import traceback
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    main.login()
    main.nav_to_stud_reg()
    try:
        await update()

    except Exception:
        print(traceback.format_exc())

        # Keep trying
        await update()
    
    finally:
        main.driver.quit()

@bot.event
async def update():
    shishi_id = 1198930964194283521
    me_id = 451301920364167179
    alaa_id = 300666842203160577

    while True:
        subjects = main.load_data()
        updates = main.write_data(subjects)
        print(updates)
        shishi_user = await bot.fetch_user(me_id)
        alaa_user = await bot.fetch_user(alaa_id)
        if updates != '':
            await shishi_user.send(updates)
            await alaa_user.send(updates)

        await asyncio.sleep(10)


if __name__ == "__main__":
    bot.run(TOKEN)