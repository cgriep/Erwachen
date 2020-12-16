import Erwachen
import discord 

TOKEN = open("Token.txt", "r").read()

intents = discord.Intents.default()
intents.members = True

erwachen = Erwachen.Umgebung()
client = discord.Client(intents=intents,chunk_guilds_at_startup=True,guild_subscriptions=True)

@client.event 
async def on_message(message):
    # nicht auf Nachrichten des Bots reagieren
    if message.author == client.user:
        return
    if message.content == '7!':
        await erwachen.schreibeNachricht(message, 'siebääähn!')
    else:
        await erwachen.befehl(message)

@client.event
async def on_raw_message_delete(message):
    # löschen einer alten Nachricht
    if message.cached_message == None:
        channel = client.get_channel(message.channel_id)
        guild = client.get_guild(message.guild_id)
        print ( 'Eine Nachricht wurde gelöscht')
        #await erwachen.loggeLoeschen(None, msg)

@client.event
async def on_message_delete(message):
    # lschen einer gecachten Nachricht
    await erwachen.loggeLoeschen(message)

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hallo {member.name}, wünsche wohl erwacht zu sein!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


client.run(TOKEN)
