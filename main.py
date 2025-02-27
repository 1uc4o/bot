import discord
import requests
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 123456789012345678  # Substitua pelo ID do canal

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.message_content = True

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
    """Função que pega o preço do Bitcoin"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url).json()
    price = response["bitcoin"]["usd"]
    change = response["bitcoin"]["usd_24h_change"]
    return price, change

async def send_bitcoin_update():
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(CHANNEL_ID)
    if not channel:
        print("❌ Canal inválido! Verifique o ID.")
        return
    while not bot.is_closed():
        try:
            price, change = await get_bitcoin_price()
            status = "subiu" if change > 0 else "caiu"
            await channel.send(f"🪙 Bitcoin agora: ${price:.2f}\n📉 Nas últimas 24h, {status} {abs(change):.2f}%")
            print(f"✅ Atualização do Bitcoin enviada para o canal {CHANNEL_ID}.")
        except Exception as e:
            print(f"❌ Erro ao enviar atualização do Bitcoin: {e}")
        await asyncio.sleep(3600)  # 1 hora

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    bot.loop.create_task(send_bitcoin_update())  # Inicia o loop de atualização do BTC

# Comandos do bot (mantidos iguais)
# ...

bot.run(TOKEN)