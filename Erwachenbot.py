import Erwachen
import discord 

TOKEN = ''
 
erwachen = Erwachen.Umgebung()
client = discord.Client()

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
async def on_message_delete(message):
    await erwachen.loggeLoeschen(message)

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hallo {member.name}, wünsche wohl erwacht zu sein!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


client.run(TOKEN)
