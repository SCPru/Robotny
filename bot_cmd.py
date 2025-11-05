from discord import Bot, Intents
from config import TOKEN

intents = Intents.all()
bot = Bot(intents=intents)

@bot.event
async def on_ready():
    try:
        while True:
            print(eval(input(">>> ")))
    except KeyboardInterrupt:
        pass
    
    await bot.close()

bot.run(TOKEN)