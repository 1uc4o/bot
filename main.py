import discord
import requests
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1344432335134654629

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix=["!","$"], intents=intents)

async def get_crypto_id(symbol):
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url).json()
    for coin in response:
        if coin["symbol"].lower() == symbol.lower():
            return coin["id"]
    return None

async def get_crypto_data(crypto):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd&include_market_cap=true&include_24hr_change=true&include_last_updated_at=true"
    response = requests.get(url).json()
    price = response[crypto]["usd"]
    change = response[crypto]["usd_24h_change"]
    market_cap = response[crypto]["usd_market_cap"]
    return price, change, market_cap

async def get_fear_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url).json()
    return response["data"][0]["value"]

async def get_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    response = requests.get(url).json()
    return response["data"]["market_cap_percentage"]

async def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url).json()
    price = response["bitcoin"]["usd"]
    change = response["bitcoin"]["usd_24h_change"]
    return price, change

async def send_bitcoin_update():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Canal inválido! Verifique o ID.")
        return

    while True:
        price, change = await get_crypto_data("bitcoin")
        status = "subiu" if change > 0 else "caiu"
        await channel.send(f"🪙 Bitcoin agora: ${price:.2f}\n📉 Nas últimas 24h, {status} {abs(change):.2f}%")
        await asyncio.sleep(10)  # Espera 1 hora

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} está online!')
    bot.loop.create_task(send_bitcoin_update())  # Inicia o loop de atualização do BTC

@bot.command(aliases=["preço", "btc", "bct", "Bitcoin", "bitcoin"])
async def preco(ctx):
    price = await get_crypto_data("bitcoin")
    await ctx.send(f'🪙 Bitcoin agora: ${price:.2f}')

@bot.command(aliases=["preço","preto","valor","negro","btc","bct","BTC","Btc","Bitcoin","bitcoin"])
async def preco(ctx):
    price = await get_crypto_data("bitcoin")
    await ctx.send(f'🪙 Bitcoin agora: ${price:.2f}')

@bot.command(aliases=["infobtc","infobct"])
async def info(ctx):
    price, change, market_cap = await get_crypto_data("bitcoin")
    fear_greed = await get_fear_greed_index()
    dominance = await get_dominance()
    status = "subiu" if change > 0 else "caiu"
    await ctx.send(f'🪙 Bitcoin agora: ${price:.2f}\n📉 Nas últimas 24h, {status} {abs(change):.2f}%\n💰 Market Cap: ${market_cap:.2f}\n🔥 Índice de Medo e Ganância: {fear_greed}\n🌎 Dominância BTC: {dominance["bitcoin"]:.2f}%')

@bot.command(aliases=["eth","lixo","coco","bosta","ethereum","ETH","Ethereum","Eth"])
async def infoeth(ctx):
    price, change, market_cap = await get_crypto_data("ethereum")
    fear_greed = await get_fear_greed_index()
    dominance = await get_dominance()
    status = "subiu" if change > 0 else "caiu"
    await ctx.send(f'💎 Ethereum agora: ${price:.2f}\n📉 Nas últimas 24h, {status} {abs(change):.2f}%\n💰 Market Cap: ${market_cap:.2f}\n🔥 Índice de Medo e Ganância: {fear_greed}\n🌎 Dominância ETH: {dominance["eth"]:.2f}%')

@bot.command(aliases=["solana","sol","Solana","SOL","Sol"])
async def infosol(ctx):
    price, change, market_cap = await get_crypto_data("solana")
    fear_greed = await get_fear_greed_index()
    dominance = await get_dominance()
    status = "subiu" if change > 0 else "caiu"
    await ctx.send(f'☀️ Solana agora: ${price:.2f}\n📉 Nas últimas 24h, {status} {abs(change):.2f}%\n💰 Market Cap: ${market_cap:.2f}\n🔥 Índice de Medo e Ganância: {fear_greed}\n🌎 Dominância SOL: {dominance["sol"]:.2f}%')

@bot.command(aliases=["top"])
async def ranking(ctx):
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    response = requests.get(url).json()

    ranking_message = "🏆 **Top 10 Criptos por Market Cap:**\n"

    for coin in response[:10]:  # Garantindo que apenas os 10 primeiros sejam considerados
        ranking_message += f'{coin["market_cap_rank"]}. {coin["name"]} (${coin["current_price"]:.2f}) - Market Cap: ${coin["market_cap"]:.2f}\n'

    await ctx.send(ranking_message)

@bot.command(aliases=["comandos"])
async def comando(ctx):
    commands_list = "**Comandos disponíveis:**\n\n"
    commands_list += "!preco - Mostra o preço do Bitcoin\n"
    commands_list += "!info - Informações detalhadas sobre o Bitcoin\n"
    commands_list += "!eth - Informações detalhadas sobre o Ethereum\n"
    commands_list += "!sol - Informações detalhadas sobre a Solana\n"
    commands_list += "!ranking - Exibe as 10 maiores criptos por Market Cap\n"
    commands_list += "!moeda [nome] - Informações detalhadas sobre qualquer criptomoeda\n"
    await ctx.send(commands_list)

@bot.command()
async def moeda(ctx, nome: str):
    nome = nome.lower()
    moeda_id = await get_crypto_id(nome)

    if not moeda_id:
        await ctx.send(f'❌ Moeda "{nome.upper()}" não encontrada. Verifique o nome e tente novamente.')
        return

    try:
        price, change, market_cap = await get_crypto_data(moeda_id)
        fear_greed = await get_fear_greed_index()
        status = "subiu" if change > 0 else "caiu"
        await ctx.send(f'🔍 {nome.upper()} agora: ${price:.2f}\n📉 Nas últimas 24h, {status} {abs(change):.2f}%\n💰 Market Cap: ${market_cap:.2f}\n🔥 Índice de Medo e Ganância: {fear_greed}')
    except requests.exceptions.RequestException as e:
        await ctx.send(f'❌ Erro ao buscar dados da moeda "{nome.upper()}". Tente novamente mais tarde.')
    except KeyError:
        await ctx.send(f'❌ Moeda "{nome.upper()}" não encontrada. Verifique o nome e tente novamente.')

bot.run(TOKEN)
