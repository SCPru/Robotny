from discord import Bot, ApplicationContext, Message, Embed, Colour, Intents
from discord.commands import Option
from yarl import URL

from search import Searcher
from config import config, DEBUG
from logger import get_logger

intents = Intents.all()
bot = Bot(intents=intents)
searcher = Searcher()

logger = get_logger(config("logs_dir"), DEBUG)

async def get_search_embed(query: str):
    search_results = await searcher.search(f"site:{config("site")} {query}")

    if not search_results:
        return None

    results = []
    for title, link in search_results:
        path = URL(link).path

        prefixes = {
            "Обсуждение: ": path.startswith("/forum/") or "/comments/show" in path,
            "Черновик: ": path.startswith("/draft:"),
            "Полигон: ": path.startswith("/sandbox:"),
            "Удалено: ": path.startswith("/deleted:"),
            "Пользователь: ": path.startswith("/-/users/"),
        }

        result = f"[{title}]({link})"
        
        for prefix, condition in prefixes.items():
            if condition:
                result = f"{prefix}{result}"

        results.append(result)

    embed = Embed(
        title=config("search.report.title"),
        description="\n".join(results),
        color=Colour.blurple()
    )

    return embed

@bot.event
async def on_connect():
    logger.info(f"Запускаю {config("name")} v{config("version")}")
    await bot.sync_commands()
    await searcher.start_client()

@bot.event
async def on_disconnect():
    logger.info(f"Соединение с Discord утеряно")

@bot.event
async def on_resumed():
    logger.info(f"Соединение с Discord восcтановлено")

@bot.event
async def on_ready():
    logger.info(f"{config("name")} v{config("version")} готов к работе")

@bot.listen("on_message")
async def handle_text_searc(message: Message):
    if message.author == bot.user:
        return
    
    if message.content.startswith("? "):
        query = message.content[2:]
        embed = await get_search_embed(query)

        if embed:
            await message.reply(embed=embed, mention_author=False)
        else:
            error_message = config("search.report.error_message")
            await message.reply(error_message, mention_author=False)

@bot.slash_command(
        name=config("commands.search.name"),
        description=config("commands.search.description.default"),
        description_localizations=config("commands.search.description.localizations")
)
async def cmd_search(
    ctx: ApplicationContext, 
    query: Option(
        str, 
        description=config("commands.search.arguments.query.description.default"),
        description_localizations=config("commands.search.arguments.query.description.localizations"),
        required=True) # type: ignore
    ):
    
    embed = await get_search_embed(query)

    if embed:
        await ctx.respond(embed=embed)
    else:
        error_message = config("search.report.error_message")
        await ctx.respond(error_message)
