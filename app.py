from discord import Bot, ApplicationContext, Member, Message, Embed, Colour, Intents, Message, Guild, default_permissions, guild_only
from discord.commands import Option
from random import choice
from yarl import URL

import re

from search import Searcher
from config import config, DEBUG, GOOGLE_SEARCH_API_KEYS
from logger import get_logger


intents = Intents.all()
bot = Bot(intents=intents)
searcher = Searcher(
    api_keys=GOOGLE_SEARCH_API_KEYS,
    engine_id=config('search.engine_id')
)

logger = get_logger(config('logs_dir'), DEBUG)

PUNCTUASSERY_PATTERN = re.compile(config('punctuassery.match'))


def is_accepted_on_server(server):
    accepted_servers =  config('servers.accepted', [])
    if accepted_servers and server in accepted_servers:
        return True
    elif server not in config('servers.restricted', []):
        return True
    return False


async def get_search_embed(query: str, page: int=1):
    search_results = await searcher.search(
        query=query,
        offset=(page-1)*10,
        lang=config('search.lang'),
        timeout=config('search.timeout')
    )

    if not search_results:
        return None

    results = []
    for title, link in search_results:
        path = URL(link).path

        prefixes = {
            'Обсуждение: ': path.startswith('/forum/') or '/comments/show' in path,
            'Черновик: ': path.startswith('/draft:'),
            'Полигон: ': path.startswith('/sandbox:'),
            'Удалено: ': path.startswith('/deleted:'),
            'Пользователь: ': path.startswith('/-/users/'),
        }

        result = f'[{title}]({link})'
        
        for prefix, condition in prefixes.items():
            if condition:
                result = f'{prefix}{result}'
                break

        results.append(result)

    embed = Embed(
        title=config('search.report.title'),
        description='\n'.join(results),
        color=Colour(config('search.report.embed_color'))
    )

    return embed


@bot.event
async def on_connect():
    logger.info(f'Запускаю {config('name')} v{config('version')}')
    await bot.sync_commands()
    await searcher.start_client()


@bot.event
async def on_disconnect():
    logger.info(f'Соединение с Discord утеряно')


@bot.event
async def on_resumed():
    logger.info(f'Соединение с Discord восcтановлено')


@bot.event
async def on_ready():
    logger.info(f'{config('name')} v{config('version')} готов к работе')


@bot.event
async def on_member_join(member: Member):
    newkek_role = member.guild.get_role(int(config('roles.newkek')))
    await member.add_roles(newkek_role)


@bot.listen('on_message')
async def handle_text_search(message: Message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('? '):
        query = message.content[2:]
        logger.info(f'Выполняю ? команду поиска по фразе "{query}" от пользователя {message.author}')
        embed = await get_search_embed(query)

        if embed:
            await message.reply(embed=embed, mention_author=False)
        else:
            error_message = config('search.report.error_message')
            await message.reply(error_message, mention_author=False)


@bot.listen('on_message')
async def handle_gratitude(message: Message):
    if message.author == bot.user:
        return
    
    if re.search(config('gratitudes.match'), message.content):
        await message.add_reaction(choice(config('gratitudes.reactions')))


@bot.listen('on_message')
async def handle_punctuassery(message: Message):
    if not message.guild or message.author == bot.user:
        return
    
    newkek_role = message.guild.get_role(int(config('roles.newkek')))

    if newkek_role in message.author.roles:
        test = message.content.strip().replace('\n', '').replace(' ', '')
        if re.fullmatch(PUNCTUASSERY_PATTERN, test):
            await message.delete(reason=config('punctuassery.reason'))
            logger.info(f'Удаляю срань, которую навалил {message.author}')
        else:
            await message.author.remove_roles(newkek_role)


@bot.slash_command(
    name='search',
    description=config('commands.search.description.default'),
    description_localizations=config('commands.search.description.localizations')
)
async def cmd_search(
    ctx: ApplicationContext, 
    query = Option(
        str, 
        description=config('commands.search.arguments.query.description.default'),
        description_localizations=config('commands.search.arguments.query.description.localizations'),
        required=True),
    page = Option(
        int,
        default=1,
        min_value=1,
        max_value=10,
        required=False)
    ):
    
    logger.info(f'Выполняю слеш-команду поиска по фразе "{query}" от пользователя {ctx.author}')
    embed = await get_search_embed(query, page)

    if embed:
        await ctx.respond(embed=embed)
    else:
        error_message = config('search.report.error_message')
        await ctx.respond(error_message)


@bot.slash_command(name='fox')
@guild_only()
@default_permissions(manage_messages=True)
async def cmd_drug_fox(ctx: ApplicationContext):
    logger.info(f'/fox от {ctx.author}')
    await ctx.respond('👌.', ephemeral=True)
    await ctx.delete()
    await ctx.send('<:drug_fox:1304246546644209695>')


@bot.slash_command(name='say')
@guild_only()
@default_permissions(manage_messages=True)
async def cmd_drug_fox(ctx: ApplicationContext, msg: str, reply_to: Message=None, mention: bool=False):
    logger.info(f'/say "{msg}" от {ctx.author}')
    await ctx.respond('👌.', ephemeral=True)
    await ctx.delete()
    await ctx.send(msg, reference=reply_to, mention_author=mention)