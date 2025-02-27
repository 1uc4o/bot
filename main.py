import discord
import requests
import asyncio
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1344432335134654629  # ID do canal correto

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["!", "$"], intents=intents)

async def get_crypto_data(crypto):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd&include_market_cap=true&include_24hr_change=true&include_last_updated_at=true"
    response = requests.get(url).json()
    price = response[crypto]["usd"]
    change = response[crypto]["usd_24h_change"]
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
    price, _ = await get_crypto_data("bitcoin")
    await ctx.send(f'🪙 Bitcoin agora: ${price:.2f}')

bot.run(TOKEN)
