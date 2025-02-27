import discord
import requests
import asyncio
from discord.ext import commands, tasks
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1344432335134654629

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=["!", "$"], intents=intents)

API_URL = "https://api.coingecko.com/api/v3"

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    atualizar_bitcoin.start()  # Inicia o looping do Bitcoin

@tasks.loop(seconds=10)
async def atualizar_bitcoin():
    canal = bot.get_channel(CHANNEL_ID)
    if canal:
        bitcoin = buscar_moeda("bitcoin")
        if bitcoin:
            preco = bitcoin['market_data']['current_price']['usd']
            await canal.send(f"💰 Bitcoin agora: ${preco:.2f}")

def buscar_moeda(coin_id):
    url = f"{API_URL}/coins/{coin_id}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json()
    return None

@bot.command(aliases=["top10", "marketcap"])
async def ranking(ctx):
    url = f"{API_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        data = resposta.json()
        mensagem = "**Top 10 moedas por MarketCap:**\n"
        for i, moeda in enumerate(data, start=1):
            mensagem += f"{i}. {moeda['name']} (${moeda['symbol'].upper()}): ${moeda['market_cap']:,}\n"
        await ctx.send(mensagem)

@bot.command(aliases=["preço", "price","valor"])
async def preco(ctx):
    """Mostra o preço atual do Bitcoin"""
    bitcoin = buscar_moeda("bitcoin")
    if bitcoin:
        preco = bitcoin['market_data']['current_price']['usd']
        await ctx.send(f"💰 Bitcoin agora: ${preco:.2f}")
    else:
        await ctx.send("Erro ao buscar o preço do Bitcoin.")

@bot.command(aliases=["moeda", "crypto"])
async def coin(ctx, *, nome):
    """Mostra detalhes de uma criptomoeda"""
    url = f"{API_URL}/coins/markets?vs_currency=usd&ids={nome.lower()}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        data = resposta.json()
        if data:
            moeda = data[0]
            mensagem = (f"**{moeda['name']} ({moeda['symbol'].upper()})**\n"
                        f"💰 Preço: ${moeda['current_price']:.2f}\n"
                        f"📊 MarketCap: ${moeda['market_cap']:,}\n"
                        f"📉 24h: {moeda['price_change_percentage_24h']:.2f}%\n"
                        f"📈 7d: {moeda.get('price_change_percentage_7d_in_currency', 'N/A')}%\n"
                        f"📅 30d: {moeda.get('price_change_percentage_30d_in_currency', 'N/A')}%")
            await ctx.send(mensagem)
        else:
            await ctx.send("Moeda não encontrada.")

@bot.command()
async def info(ctx, *, nome):
    """Mostra detalhes de uma criptomoeda, incluindo a dominância do BTC"""
    url = f"{API_URL}/coins/{nome.lower()}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        data = resposta.json()
        market_data = data.get("market_data", {})

        if market_data:
            preco = market_data["current_price"]["usd"]
            marketcap = market_data["market_cap"]["usd"]
            volume = market_data["total_volume"]["usd"]
            btc_dominancia = market_data.get("market_cap_dominance", {}).get("btc", "N/A")

            mensagem = (f"**{data['name']} ({data['symbol'].upper()})**\n"
                        f"💰 Preço: ${preco:.2f}\n"
                        f"📊 MarketCap: ${marketcap:,}\n"
                        f"📉 Volume 24h: ${volume:,}\n"
                        f"📉 24h: {market_data.get('price_change_percentage_24h', 'N/A')}%\n"
                        f"📈 7d: {market_data.get('price_change_percentage_7d', 'N/A')}%\n"
                        f"📅 30d: {market_data.get('price_change_percentage_30d', 'N/A')}%\n"
                        f"🌍 Dominância BTC: {btc_dominancia}%")
            await ctx.send(mensagem)
        else:
            await ctx.send("Erro ao buscar os dados da moeda.")
    else:
        await ctx.send("Moeda não encontrada.")

@bot.command(aliases=["comandos", "ajuda"])
async def comando(ctx):
    comandos = ["!ranking - Mostra o top 10 moedas por marketcap",
                "!preco - Mostra o preço atual do Bitcoin",
                "!moeda <nome ou sigla> - Mostra detalhes de uma moeda",
                "!info <nome ou sigla> - Mostra detalhes de uma moeda com dominância do BTC",
                "!comando - Lista todos os comandos disponíveis"]
    await ctx.send("\n".join(comandos))

bot.run(TOKEN)