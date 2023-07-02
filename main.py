import asyncio
import json
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
    await channel.send('Started reading websocket.')
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
            async with websockets.connect('ws://derotest.friendspool.club:10301/info/',ping_interval=60, ping_timeout=120) as websocket:
                print('Connected to websocket server.')
                asyncio.ensure_future(send_ping())
                while True:
                    try:
                        result = json.loads(await websocket.recv())
                        if "wallet" in result and result["wallet"] == WALLET:
                            print("Miniblock!")
                            channel = client.get_channel(CHANNEL_DISCORD)
                            embed = discord.Embed(title="Miniblock Found!", color=0xff0000)
                            embed.set_thumbnail(url='https://docs.dero.io/assets/logo.png')
                            embed.add_field(name="Height", value=result["height"], inline=True)
                            embed.add_field(name="Timestamp", value=result["timestamp"], inline=True)
                            try:
                                await channel.send(embed=embed)
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

client.run(TOKEN_DISCORD)