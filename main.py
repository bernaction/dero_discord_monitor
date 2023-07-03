import asyncio
import json

import requests
import websockets
import discord
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Bot is ready!')
    channel = client.get_channel(CHANNEL_DISCORD)
    asyncio.ensure_future(read_websocket(channel, WALLET))

async def read_websocket(channel, WALLET):
    async def send_ping():
        while True:
                try:
                    print("ping server!")
                    await websocket.ping()
                except websockets.exceptions.ConnectionClosedError:
                    break
                await asyncio.sleep(60)
    while True:
        try:
            async with websockets.connect('ws://derotest.friendspool.club:10301/info/', ping_interval=60, ping_timeout=120) as websocket:
                print('Connected to websocket server.')
                asyncio.ensure_future(send_ping())
                while True:
                    try:
                        data = json.loads(await websocket.recv())
                        if "wallet" in data and data["wallet"] == WALLET and data["event"] == "blockMined":
                        #if "wallet" in data and data["wallet"] == 'dero1qyw28245wph625det80urwygufv23lhw8x8xajkawwdc5l0sl2l27qq2tsde9' and data["event"] == "blockMined":
                            timestamp = datetime.fromtimestamp(data["timestamp"]/1000)
                            timestamp = timestamp.strftime("%H:%M, %d/%m/%Y")
                            height = data["height"]
                            print(height)
                            await asyncio.sleep(15)
                            try:
                                headers = {'Content-Type': 'application/json', }
                                data = f'{{"jsonrpc": "2.0","id": "1","method": "DERO.GetBlock","params": {{"height": {height}}}}}'
                                r = requests.post('http://derotest.friendspool.club:10102/json_rpc', headers=headers,
                                              data=data).json()
                                reward = r["result"]["block_header"]["reward"] / 1000000
                            except:
                                print("Não foi possível pegar o reward. Utilizando o padrão.")
                                reward = 61500 / 1000000
                            cotacao = requests.get("https://api.minerstat.com/v2/coins?list=" + "DERO").json()[0]["price"]
                            #difficulty = data["difficulty"]
                            print("Miniblock!")
                            channel = client.get_channel(CHANNEL_DISCORD)
                            user = client.get_user(USER)  # eu
                            embed = discord.Embed(title=f':partying_face: \t NOVO BLOCO SOLO!\n', colour=0x0000ff)
                            embed.set_thumbnail(url='https://docs.dero.io/assets/logo.png')
                            total = reward * cotacao
                            embed.add_field(name=f':large_blue_diamond:  Valor:',
                                            value=f'Block Reward: \t{reward:.6f} DERO'
                                                  f'\nCotação:\t\t U${cotacao:.2f}'
                                                  f'\n\nTotal: U${total:.2f}'
                                                  f'\n'.replace(".", ","), inline=False)
                            embed.add_field(name=f':stopwatch: Minerado:', value=f'às {timestamp}', inline=True)
                            embed.add_field(name=":arrow_up: Altura do Bloco:", value=height, inline=True)
                            embed.add_field(name=":globe_with_meridians: Link:", value=f'https://explorer.friendspool.club/block/{height}\n\u200b', inline=False)

                            embed.set_footer(text="discord.io/BernaCripto")
                            try:
                                await channel.send(embed=embed)
                                await channel.send(f'{reward:.6f} DERO \t{user.mention}'.replace(".", ","))
                            except discord.errors.DiscordServerError as e:
                                print(f"Error sending message: {e}")
                    except websockets.exceptions.ConnectionClosedError:
                        break
                    except json.JSONDecodeError:
                        continue
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed. Retrying in 10 seconds...")
            await asyncio.sleep(10)  # Wait before reconnecting

with open('secret.json') as e:
    infos = json.load(e)

    CHANNEL_DISCORD = infos["discord"]
    WALLET = infos["wallet"]
    TOKEN_DISCORD = infos["token"]
    USER = infos['user']

client.run(TOKEN_DISCORD)


