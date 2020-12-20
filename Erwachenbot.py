import Erwachen
import discord 

TOKEN = open("Token.txt", "r").read()

intents = discord.Intents.default()
intents.members = True

erwachen = Erwachen.Umgebung()
client = discord.Client(intents=intents,chunk_guilds_at_startup=True,guild_subscriptions=True)
erwachen.client = client

@client.event 
async def on_message(message):
    # nicht auf Nachrichten des Bots reagieren
    
    if len(client.voice_clients) > 0:
      if not client.voice_clients[0].is_playing():
           await client.voice_clients[0].disconnect()
    
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
        await erwachen.loggeLoeschen(None, channel)

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
    await erwachen.LadeStartWerte()
    print(f'{client.user} has connected to Discord!')
    # setze Avatar-Bild
    try:
      with open('hal.jpg', 'rb') as f:
        await client.user.edit(avatar=f.read())
    except:
      print('Fehler beim Avatar-setzen')
    # Spiel initialisieren soweit notwendig
    for guild in client.guilds:
      print (f'Initialisiere {guild.name}')
      category = discord.utils.find(lambda m: m.name=='Konsolen', guild.categories)
      if category is None:
        await guild.create_category('Konsolen')
        print ('Kategorie Konsolen erstellt')
      category = discord.utils.find(lambda m: m.name=='Orte', guild.categories)
      if category is None:
        category = await guild.create_category('Orte')
        print ('Kategorie Orte erstellt')
      channel = dest = discord.utils.find(lambda m: m.name=="Aufwachraum" and m.category.name=='Orte', guild.voice_channels)
      if channel is None:
        channel = await guild.create_voice_channel("Aufwachraum", category=category)
        overwrites = channel.overwrites_for(guild.default_role)
        overwrites.speak = False
        overwrites.view_channel = False
        overwrites.connect = False 
        await channel.set_permissions(guild.default_role, overwrite=overwrites, reason='Spielinitialisierung')            
      channel = discord.utils.get(guild.text_channels, name='start-portal')
      if channel is None:
        category = discord.utils.find(lambda m: m.name=='Textkanäle', guild.categories)
        dest = await guild.create_text_channel(f'start-portal', category=category)
        print ('Kanal Startportal erstellt')
        await dest.send('**Bei diesem Kanal handelt es sich um ein Online-Rollenspiel.**\n\n' +
          'Du spielst einen fiktiven Charakter in einer fernen Zukunft. Im Prinzip startet jeder im "Nichts". Du wachst auf und befindest dich allein in einem kleinen Raum.\n' +
          'Alle weiteren Informationen bezüglich des Genres, deiner Person, deinen Fähigkeiten und Fertigkeiten, dem Umfeld, usw. musst oder kannst du dir erspielen.\n\n'+ 
          '***Wichtigste Spielregel:***\n' + 
          'Das System entscheidet alles und hat immer Recht (naja, das wird sich noch herausstellen).\n\n' +
          '**Kommunikation**\n' +
          'Für jeden Spieler wird ein eigener Textkanal, Konsole genannt, erstellt. Dieser ist normalerweise *nur* von dir und dem System einzusehen. Hier kannst du mit dem System interagieren und solltest dein Logbuch führen, d.h. Erkenntnisse, Erfahrungen, erspielte Gegenstände und alle anderen InTime-relevanten Dinge hinterlegen, damit du und das System auf gleichem Wissenstand sind. Beginne Logbucheinträge mit "#", damit das System sie nicht als Kommandos interpretiert. Daraus und durch die mögliche Interaktion mit anderen entwickelt sich das Spiel.\n\n'+
          'Zudem gibt es Sprachkanäle, die die einzelnen Orte im Spiel repräsentieren. Du musst dich in einem Orts-Sprachkanal befinden, um im Spiel interagieren zu können.\n'+ 
          '**Charaktererstellung**\n'+
          'Wenn du mitspielen möchtest, wähle bitte einen Fantasienamen und gebe *Teilnehmen <neuername>* ein. Das System ändert deinen angezeigten Namen auf diesem Server entsprechend.\n' +
          '*Hinweis:*\n'+
          'Du wirst nach Beginn des Spiels nicht mehr in diesen Kanal zurückkehren können.\n\n' +
          '**FAQs, Infos und sonstiges**\n' +
          'Alles unter "Textkanäle" steht zur allgemeinen Kommunikation zur Verfügung. Es sind ein reiner OutTime-Kanäle, d.h. hier sollten keine Informationen ausgestauscht werden, die sich auf Inhalte aus den Spielsituationen ergeben. Aber man kann hier z.B. Termine vereinbaren, Verständnisfragen äußern, etc.\n' +
          'Das Spiel läuft in den Kategorien "Orte" und "Konsolen" ab.\n' +
          'Achte darauf, dich mit einem der Spielkanäle zu verbinden, falls du in ein laufendes Spiel zurückkehrst.\n' +
          '**Begriffe**\n' +
          '> "InTime" = alles was im Spiel geschieht\n' +
          '> "OutTime" = alles was nichts mit dem Spielinhalt zu tun hat')
    print ('System bereit')

client.run(TOKEN)
