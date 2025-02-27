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

bot = commands.Bot(command_prefix=["!", "$"], intents=intents)

API_URL = "https://api.coingecko.com/api/v3"

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    print(f"Mensagem recebida: {message.content} de {message.author}")

    # Permite que os comandos ainda funcionem corretamente
    await bot.process_commands(message)

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

@bot.command()
async def info(ctx, *, nome):
    """Mostra detalhes de uma criptomoeda, incluindo a dominância do BTC"""
    # Buscar a lista de moedas para mapear siglas para nomes
    lista_url = f"{API_URL}/coins/list"
    lista_resposta = requests.get(lista_url)
    
    if lista_resposta.status_code == 200:
        moedas = lista_resposta.json()
        nome = nome.lower()

        # Tenta encontrar a moeda pelo ID ou pela sigla
        moeda_id = None
        for moeda in moedas:
            if moeda["id"] == nome or moeda["symbol"].lower() == nome:
                moeda_id = moeda["id"]
                break
        
        if not moeda_id:
            await ctx.send("Moeda não encontrada.")
            return
        
        # Buscar os dados da moeda pelo ID encontrado
        url = f"{API_URL}/coins/{moeda_id}"
        resposta = requests.get(url)
        
        if resposta.status_code == 200:
            data = resposta.json()
            market_data = data.get("market_data", {})

            if market_data:
                preco = market_data["current_price"]["usd"]
                marketcap = market_data["market_cap"]["usd"]
                volume = market_data["total_volume"]["usd"]
                mensagem = (f"**{data['name']} ({data['symbol'].upper()})**\n"
                            f"💰 Preço: ${preco:.2f}\n"
                            f"📊 MarketCap: ${marketcap:,}\n"
                     

@bot.command(aliases=["comandos", "ajuda"])
async def comando(ctx):
    comandos = ["!ranking - Mostra o top 10 moedas por marketcap",
                "!preco - Mostra o preço atual do Bitcoin",
                "!info <nome ou sigla> - Mostra detalhes de uma moeda com dominância do BTC",
                "!comando - Lista todos os comandos disponíveis"]
    await ctx.send("\n".join(comandos))

bot.run(TOKEN)