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

bot = commands.Bot(command_prefix=["!", "$"], intents=intents)

API_URL = "https://api.coingecko.com/api/v3"

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    asyncio.create_task(atualizar_bitcoin())  # Corrigido para rodar sem bloquear comandos

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    print(f"Mensagem recebida: {message.content} de {message.author}")

    # Permite que os comandos ainda funcionem corretamente
    await bot.process_commands(message)

async def atualizar_bitcoin():
    """Loop infinito para enviar o preço do Bitcoin a cada 10s"""
    await bot.wait_until_ready()  # Espera o bot estar pronto
    canal = bot.get_channel(CHANNEL_ID)
    while not bot.is_closed():  # Mantém o loop rodando sempre
        if canal:
            bitcoin = buscar_moeda("bitcoin")
            if bitcoin:
                preco = bitcoin['market_data']['current_price']['usd']
                await canal.send(f"💰 Bitcoin agora: ${preco:.2f}")
        await asyncio.sleep(10)  # Espera 10 segundos antes de repetir

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

@bot.command(aliases=["preço", "price", "valor"])
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
    lista_url = f"{API_URL}/coins/list"
    lista_resposta = requests.get(lista_url)
    
    if lista_resposta.status_code == 200:
        moedas = lista_resposta.json()
        nome = nome.lower()

        moeda_id = None
        for moeda in moedas:
            if moeda["id"] == nome or moeda["symbol"].lower() == nome:
                moeda_id = moeda["id"]
                break
        
        if not moeda_id:
            await ctx.send("Moeda não encontrada.")
            return
        
        url = f"{API_URL}/coins/{moeda_id}"
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
            await ctx.send("Erro ao buscar os dados da moeda.")
    else:
        await ctx.send("Erro ao acessar a lista de moedas.")

@bot.command(aliases=["comandos", "ajuda"])
async def comando(ctx):
    comandos = ["!ranking - Mostra o top 10 moedas por marketcap",
                "!preco - Mostra o preço atual do Bitcoin",
                "!info <nome ou sigla> - Mostra detalhes de uma moeda com dominância do BTC",
                "!comando - Lista todos os comandos disponíveis"]
    await ctx.send("\n".join(comandos))

bot.run(TOKEN)
