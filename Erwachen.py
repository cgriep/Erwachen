import discord
import ast
import csv
import json
import sys

class Umgebung:
    async def fehler(self, msg):
        await self.schreibeNachricht(msg, "Unbekanntes Kommando.")
        pass

    async def befehl(self, msg):
        # nur in Spielchannels reagieren
        if msg.channel.name == 'start-portal' or msg.channel.name.startswith('konsole-'):
            eingaben = msg.content.split(' ')
            if msg.channel.name == 'start-portal' and eingaben[0] != 'Teilnehmen':
                return
            if eingaben[0] in dir(Umgebung):
                return await getattr(self, eingaben[0], lambda fehler: "unbekannt")(msg)
            else:
                await self.fehler(msg)
        else:
            print('Channel '+msg.channel.name+' ignoriert')

    def __init__(self):
        self.LadeStartWerte()
        print('Startwerte gelesen')
        print(self.Werte)

    # Laed Werte aus einer gespeicherten Session
    def LadeWerte(self, msg):
        self.Werte = []
        with open(self.parameter(msg, 1), 'r') as json_file:
            self.Werte = json.load(json_file)

    def SchreibeWerte(self, msg):
        with open(self.parameter(msg, 1), 'w') as json_file:
            json.dump(self.Werte, json_file)

    # laed die CSV Datei mit den Startwerten
    def LadeStartWerte(self, msg=None):
        self.Werte = []
        with open('Initialwerte.csv', 'r') as datei:
            reader = csv.reader(datei, delimiter = ',')
            self.Werte = {rows[0]:float(rows[1]) for rows in reader}
        self.Werte['Klick'] = 0

    #
    def parameter(self, msg, nr=9999):
        eingaben = msg.content.split(' ')
        if len(eingaben)-1 < nr:
            return 'Fehler'
        else:
            return eingaben[nr].strip()

    # Wert mit Überprüfung setzen
    async def setzeWert(self, msg, wertname=None, wert='', pruefwertname=''):
        if not wert.isnumeric():
            await self.schreibeNachricht(msg,f'Der Wert "{wert}" ist ungültig. Kommando nicht ausführbar.')
            return(False)
        wert = float(wert)
        if pruefwertname != '':
            if (wert > self.Werte[pruefwertname]) or (wert < 0):
                await self.schreibeNachricht(msg,f'Der Wert {wert} ist nicht erlaubt. Kommando nicht ausführbar.')
                return(False)
        self.Werte[wertname] = wert
        await self.schreibeNachricht(msg,f'Der Wert {wert} wurde gesetzt. ')
        return(True)

    async def Wert(self, msg):
        par = self.parameter(msg, 2)
        name = self.parameter(msg, 1)
        if name == 'Fehler':
            await fehler(msg)
        else:
            if par == 'Fehler':
                await self.schreibeNachricht(msg,name+'= '+str(self.Werte[name]))
            else:
                await self.setzeWert(msg, name, par)

    async def aendereWert(self, msg, bezeichnung=None):
        await self.setzeWert(msg, f'Energieverbrauch_{bezeichnung}', self.parameter(msg,1), f'Energieverbrauch_{bezeichnung}_max')

    async def Anzeige(self, msg, bezeichnung=None, text=None):
        if bezeichnung is None:
          self.schreibeNachricht(msg, 'Unbekannter Befehl.')
        if text is None:
            text = bezeichnung
        text = f'{text}energie ist eingestellt auf ' + str(self.Werte[f'Energieverbrauch_{bezeichnung}'] ) + ' von ' + str(self.Werte[f'Energieverbrauch_{bezeichnung}_max'])
        await self.schreibeNachricht(msg,text)

    # Spielbefehle Anzeige / Wertänderung
    async def GeneratorEnergie(self, msg):
        await self.aendereWert(msg, 'Generator')

    async def GeneratorAnzeige(self, msg):
        await self.Anzeige(msg, 'Generator')

    async def RecyclingAnzeige(self, msg):
        await self.Anzeige(msg, 'Recycling')

    async def RecyclingEnergie(self, msg):
        await self.aendereWert(msg, 'Recycling')

    async def AquaAnzeige(self, msg):
        await self.schreibeNachricht(msg,f'Energieverbrauch Aquaristikmodul: ' +
                                       str(self.Werte['Energieverbrauch_Aqua']) +
                                       ' von '+
                                       str(self.Werte['Energieverbrauch_Aqua_max']) +
                                       '\n' +
                                       'Anteil Luft-/Nahrungserzeugung: ' +
                                       str(float(self.Werte['Energieanteil_Aqua_Lufterzeugung']) * 100) +
                                       '%'  )

    async def AquaEnergie(self, msg):
        await self.aendereWert(msg, 'Aqua')

    async def BioEnergie(self, msg):
        await self.aendereWert(msg, 'Bio')

    async def BioAnzeige(self, msg):
        await self.schreibeNachricht(msg,f'Energieverbrauch Biotopmodul: ' +
                                       str(self.Werte['Energieverbrauch_Bio']) +
                                       ' von '+
                                       str(self.Werte['Energieverbrauch_Bio_max']) +
                                       '\n' +
                                       'Anteil Luft-/Nahrungserzeugung: ' +
                                       str(float(self.Werte['Energieanteil_Bio_Lufterzeugung']) * 100) +
                                       '%'  )

    async def AussenhuelleEnergie(self, msg):
        await self.aendereWert(msg, 'Aussenhuelle')

    async def AussenhuelleAnzeige(self, msg):
        await self.Anzeige(msg, 'Aussenhuelle', 'Außenhülle')

    async def LufttankEnergie(self, msg):
        await self.aendereWert(msg, 'Lufttank')

    async def LufttankAnzeige(self, msg):
        await self.Anzeige(msg, 'Lufttank')

    async def KuehlmodulEnergie(self, msg):
        await self.aendereWert(msg,'Kuehlmodul')

    async def KuehlmodulAnzeige(self, msg):
        await self.Anzeige(msg,'Kuehlmodul', 'Kühlmodul')

    async def ServerraumEnergie(self, msg):
        await self.aendereWert(msg,'Serverraum')

    async def ServerraumAnzeige(self, msg):
        await self.Anzeige(msg,'Serverraum')

    async def KrankenstationEnergie(self, msg):
        await self.aendereWert(msg,'Krankenstation')

    async def KrankenstationAnzeige(self, msg):
        await self.Anzeige(msg,'Krankenstation')

    async def LagerEnergie(self, msg):
        await self.aendereWert(msg,'Lager')

    async def LagerAnzeige(self, msg):
        await self.Anzeige(msg,'Lager')

    async def MultiEnergie(self, msg):
        await self.aendereWert(msg,'Multi')

    async def MultiAnzeige(self, msg):
        await self.Anzeige(msg,'Multi')

    async def KommandoEnergie(self, msg):
        await self.aendereWert(msg,'Kommando')

    async def KommandoAnzeige(self, msg):
        await self.Anzeige(msg,'Kommando')

    async def GeheimlaborEnergie(self, msg):
        await self.aendereWert(msg,'Geheimlabor')

    async def GeheimlaborAnzeige(self, msg):
        await self.Anzeige(msg,'Geheimlabor')

    async def MesseEnergie(self, msg):
        await self.aendereWert(msg,'Messe')

    async def MesseAnzeige(self, msg):
        await self.Anzeige(msg,'Messe')

    async def EnergiespeicherEnergie(self, msg):
        await self.aendereWert(msg,'Energiespeicher')

    async def EnergiespeicherAnzeige(self, msg):
        await self.Anzeige(msg,'Energiespeicher')

    async def BrennstofflagerEnergie(self, msg):
        await self.aendereWert(msg,'Brennstofflager')

    async def BrennstofflagerAnzeige(self, msg):
        await self.Anzeige(msg,'Brennstofflager')

    async def ForschungsmodulEnergie(self, msg):
        await self.aendereWert(msg,'Forschungsmodul')

    async def ForschungsmodulAnzeige(self, msg):
        await self.Anzeige(msg,'Forschungsmodul')

    async def SolarEnergie(self, msg):
        await self.aendereWert(msg,'Solar')

    async def SolarAnzeige(self, msg):
        await self.Anzeige(msg,'Solar')

    async def ZeigeStatus(self, msg):
        await self.schreibeNachricht(msg,f' *** System-Status *** || *Klick ' + str(self.Werte['Klick']) + '* \n ' +
                'Energie      = '+ str(self.Werte['Energie']) + ' von maximal: ' + str(self.Werte['Energie_max']) + ' \n ' +
                'Brennstoff = ' + str(self.Werte['Brennstoff']) + ' von maximal: ' + str(self.Werte['Brennstoff_max']) + ' \n' +
                'Nahrung     = ' + str(self.Werte['Nahrung']) + ' von maximal: ' + str(self.Werte['Nahrung_max']) + ' \n ' +
                'Luft             = ' + str(self.Werte['Luft']) + ' von maximal: ' + str(self.Werte['Luft_max']) )

    # Spiellogiken
    async def AquaStart(self, msg):
        self.Werte['Energie']    -= self.Werte['Energieverbrauch_Aqua'] * (2-self.Werte['Techstufe_Facility'])
        self.Werte['Luft']       += self.Werte['Energieverbrauch_Aqua'] * self.Werte['Energieanteil_Aqua_Lufterzeugung'] * self.Werte['Techstufe_Aqua'] * self.Werte['Lufterzeugung_Anpassungsfaktor']
        self.Werte['Nahrung']    += self.Werte['Energieverbrauch_Aqua'] * (1-self.Werte['Energieanteil_Aqua_Lufterzeugung'])*self.Werte['Techstufe_Aqua']*self.Werte['Nahrungs_Anpassungsfaktor']
        self.Werte['Brennstoff'] -= self.Werte['Energieverbrauch_Aqua'] * (2-self.Werte['Techstufe_Recycling'])


    async def AussenhuelleStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Aussenhuelle']*(2-self.Werte['Techstufe_Technik'])


    async def BioStart(self, msg):
        self.Werte['Energie']       -= self.Werte['Energieverbrauch_Bio'] * (2-self.Werte['Techstufe_Facility'])
        self.Werte['Luft']          += self.Werte['Energieverbrauch_Bio'] * self.Werte['Energieanteil_Bio_Lufterzeugung'] * self.Werte['Techstufe_Bio'] * self.Werte['Lufterzeugung_Anpassungsfaktor']
        self.Werte['Nahrung']       += self.Werte['Energieverbrauch_Bio'] * (1-self.Werte['Energieanteil_Bio_Lufterzeugung'])*self.Werte['Techstufe_Bio']*self.Werte['Nahrungs_Anpassungsfaktor']
        self.Werte['Brennstoff']    -= self.Werte['Energieverbrauch_Bio'] * (2-self.Werte['Techstufe_Recycling'])



    async def ForschungsmodulStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Forschungsmodul']*(2-self.Werte['Techstufe_Ingenieur'])


    async def GeheimlaborStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Geheimlabor']*(2-self.Werte['Techstufe_Kollaborateur'])

    async def GeheimlagerStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Geheimlager']*(2-self.Werte['Techstufe_Kollaborateur'])

    async def GeneratorStart(self, msg):
        self.Werte['Brennstoff'] -= self.Werte['Energieverbrauch_Generator']*(2-self.Werte['Techstufe_Ingenieur'])
        self.Werte['Energie']    += self.Werte['Energieverbrauch_Generator']*self.Werte['Generatorfaktor']*self.Werte['Techstufe_Ingenieur']-self.Werte['Energieverbrauch_Generator']

    async def MesseStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Messe']*(2-self.Werte['Techstufe_Facility'])

    async def KommandoStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Kommando']*(2-self.Werte['Techstufe_Facility'])

    async def KrankenstationStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Krankenstation']*self.Werte['Krankenstationfaktor'] - self.Werte['Energieverbrauch_Krankenstation']*self.Werte['Techstufe_Facility']

    async def LagerStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Lager']*(2-self.Werte['Techstufe_Facility'])

    async def MultiStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Multi']*(2-self.Werte['Techstufe_Facility'])

    async def ServerraumStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Serverraum']*(2-self.Werte['Techstufe_Informatik'])

    async def SolarStart(self, msg):
        self.Werte['Energie'] += self.Werte['Energieverbrauch_Solar']*self.Werte['Techstufe_Technik']*self.Werte['Solarfaktor'] - self.Werte['Energieverbrauch_Solar']

    async def RecyclingStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Recycling']*(2-self.Werte['Techstufe_Recycling'])
        self.Werte['Luft'] -= self.Werte['Energieverbrauch_Recycling']*(2-self.Werte['Techstufe_Recycling'])
        self.Werte['Brennstoff'] += self.Werte['Energieverbrauch_Recycling']*self.Werte['Brennstoff_Anpassungsfaktor']*self.Werte['Techstufe_Recycling']


    # Lager/ Systemwerte

    async def EnergiespeicherStart(self, msg):
        self.Werte['Energie']    -= self.Werte['Energieverbrauch_Energiespeicher']*(2-self.Werte['Techstufe_Facility']) + self.Werte['Energieverbrauch_Verluste']
        self.Werte['Energie_max'] = (self.Werte['Energiespeicher_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Energiespeicher_max']*0.2*self.Werte['Energieverbrauch_Energiespeicher'])

    async def KuehlmodulStart(self, msg):
        self.Werte['Energie']    -= self.Werte['Energieverbrauch_Kuehlmodul']*(2-self.Werte['Techstufe_Facility'])
        self.Werte['Nahrung_max'] = (self.Werte['Nahrungsspeicher_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Nahrungsspeicher_max']*0.2*self.Werte['Energieverbrauch_Kuehlmodul'])
        self.Werte['Nahrung']    -= self.Werte['Nahrungsverbrauch_proZyklus']

    async def LufttankStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Lufttank']*(2-self.Werte['Techstufe_Technik'])
        self.Werte['Luft_max'] = (self.Werte['Lufttank_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Lufttank_max']*0.2*self.Werte['Energieverbrauch_Lufttank'])
        self.Werte['Luft']    -= self.Werte['Luftverbrauch_Geheimlabor'] + self.Werte['Luftverbrauch_Module'] 

    async def BrennstofflagerStart(self, msg):
        self.Werte['Energie']       -= self.Werte['Energieverbrauch_Brennstofflager']*(2-self.Werte['Techstufe_Technik'])
        self.Werte['Brennstoff_max'] = (self.Werte['Brennstoff_tankvolumen_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Brennstoff_tankvolumen_max']*0.2*self.Werte['Energieverbrauch_Brennstofflager'])



    async def ZugEnde(self, msg):
        await self.GeneratorStart(msg)
        await self.BioStart(msg)
        await self.AquaStart(msg)
        await self.RecyclingStart(msg)
        await self.AussenhuelleStart(msg)
        await self.ForschungsmodulStart(msg)
        await self.KrankenstationStart(msg)
        await self.LagerStart(msg)
        await self.MultiStart(msg)
        await self.KommandoStart(msg)
        await self.GeheimlaborStart(msg)
        await self.GeheimlagerStart(msg)

        await self.MesseStart(msg)
        await self.ServerraumStart(msg)
        await self.EnergiespeicherStart(msg)
        await self.KuehlmodulStart(msg)
        await self.LufttankStart(msg)
        await self.BrennstofflagerStart(msg)
        await self.SolarStart(msg)


        self.Werte['Klick'] += 1
        await self.ZeigeStatus(msg)
        if (self.Werte['Energie'] < 0) or (self.Werte['Luft'] < 0) or (self.Werte['Nahrung'] < 0) or (self.Werte['Brennstoff'] < 0):
                 await self.schreibeNachricht(msg,f'Die Resourcen sind zuende gegangen!')

    async def Teilnehmen(self, msg):
        if msg.channel.name != 'start-portal':
            return
        # prüfen ob channel schon da ist
        name = self.parameter(msg, 1).strip().lower()
        # channel erzeugen
        channel = discord.utils.get(msg.guild.text_channels, name='konsole-'+name)
        if channel is not None:
            await self.schreibeNachricht(msg, 'Zugriff für diesen Namen verweigert. Wähle einen anderen.')
        else:
            category = discord.utils.find(lambda m: m.name=='Konsolen', msg.guild.categories)
            overwrites = {
                    msg.author: discord.PermissionOverwrite(send_messages=True, read_messages=True),
                    msg.guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=False),
                    msg.guild.me: discord.PermissionOverwrite(send_messages=True, read_messages=True)
                    }
            dest = await msg.guild.create_text_channel(f'konsole-{name}', overwrites=overwrites, category=category)
            await dest.send(f'Willkommen {name}. Wünsche wohl geruht zu haben.')
            # nickname ändern - funktioniert nur bei normalen Benutzern, nicht bei Admins!
            try:
                await msg.author.edit(nick = name)
                await dest.send(f'Nickname wurde geändert.')
            except:
                await self.schreibeNachricht(msg, f'Nickname des priviligierten Accounts konnte nicht geändert werden.')
            perms = msg.channel.overwrites_for(msg.author)
            perms.write_messages=False
            perms.read_messages=False
            await msg.channel.set_permissions(msg.author, overwrite=perms, reason="Teilnehmen-Command")
            # entferne die Teilnahme-Nachricht
            await msg.delete()
            
    async def Bewegen(self, msg):
        try:
          ch = msg.author.voice.channel
          if ch is None:
            raise ValueError('Kein Sprachkanal vorhanden.')
        except:
             await self.schreibeNachricht(msg, 'Bewegen ohne Sprachverbindung ist nicht möglich. Bitte erst verbinden.')
             return
        if ch.category.name != 'Orte':
            await self.schreibeNachricht(msg,' Bewegen nur mit Sprachverbindung in einem Ort möglich.')
            return
        server = msg.guild
        channel = self.parameter(msg, 1).strip()
        if channel == ch.name:
            await self.schreibeNachricht(msg,' Ort ist bereits erreicht.')
            return
    
        # Bewegung nur in bekannte und aktivierte Module
        try:
            if self.Werte['Modul_'+channel] == 1:
                dest = discord.utils.find(lambda m: m.name==channel and m.category.name=='Orte', server.voice_channels)
                text = ''
                overwrites = {
                            msg.author: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
                            }
                if dest is None:
                    name = msg.author.nick
                    category = discord.utils.find(lambda m: m.name=='Orte', server.categories)
                    dest = await server.create_voice_channel(channel, overwrites=overwrites, category=category)
                    text = 'als erster '
                else:
                       perms = dest.overwrites_for(msg.author)
                       perms.connect=True
                       perms.speak=True
                       perms.view_channel=True
                       await dest.set_permissions(msg.author, overwrite=perms, reason="Bewegen-Command")
                try:
                  if msg.author.voice is not None:
                    ch = msg.author.voice.channel
                    if ch is not None:
                      if ch.category.name=='Orte':
                        await self.schreibeNachricht(msg, f'{msg.author.nick} verlässt {msg.author.voice.channel} und betritt {text}{channel}')
                        perms = msg.author.voice.channel.overwrites_for(msg.author)
                        perms.connect=False
                        perms.speak=False
                        perms.view_channel=False
                        await msg.author.voice.channel.set_permissions(msg.author, overwrite=perms, reason="Bewegen-Command")
                      else:
                        await self.schreibeNachricht(msg, f'{msg.author.nick} betritt {text}{channel} von ausserhalb kommend')
                    else:
                      await self.schreibeNachricht(msg, f'{msg.author.nick} betritt {text}{channel}, ist aber nicht verbunden')
                      
                  else:
                      await self.schreibeNachricht(msg, f'{msg.author.nick} betritt {text}{channel} ohne Sprachverbindung.')
                      return True
                except:
                  await self.schreibeNachricht(msg, 'Fehler beim Sprachkanal')
                await msg.author.move_to(dest, reason='betritt den Raum')                
            else:
                await self.schreibeNachricht(msg, 'Modul unbekannt oder deaktiviert.')
        except KeyError:
            await self.schreibeNachricht(msg,'Unbekannter Raum')

    async def Konsole(self, msg):
        name = self.parameter(msg, 1)
        text = self.parameter(msg, 2)
        if name != 'Fehler' and text != 'Fehler':
            channel = discord.utils.get(msg.guild.text_channels, name='konsole-'+name)
            if channel is None:
              await self.schreibeNachricht(msg, 'Unbekannte Konsole')
              return
            await channel.send('*** Konsolennachricht: ***\n'+msg.content[(len(name)+1+7+1):])
        else:
            await self.schreibeNachricht(msg, 'Unbekannte Konsole')

    async def KonsoleHack(self, msg):
        name = self.parameter(msg, 1)
        anz = self.parameter(msg, 2)
        if not anz.isnumeric():
          anz = 2
        if name != 'Fehler':
            channel = discord.utils.get(msg.guild.text_channels, name='konsole-'+name)
            if channel is None:
              await self.schreibeNachricht(msg, 'Unbekannte Konsole')
              return
            text = f'***Hack Konsole {name}: ***\n'
            async for message in channel.history(limit=anz):
              text += message.content + '\n'             
            await self.schreibeNachricht(msg,text)
        else:
            await self.schreibeNachricht(msg, 'Unbekannte Konsole')

    #Hilfsfunktionen für discord

    # Nachricht mit einem Bild, picture ist Filename
    async def schreibeNachricht(self, msg, text=None, picture=None):
        if picture is None:
            await msg.channel.send(text)
        else:
            with open(picture, 'rb') as f:
               picture = discord.File(f)
               await msg.channel.send(msg.channel, picture)

    async def loggeLoeschen(self, msg):
        if msg.channel.name.startswith('konsole-'):
            if msg.author.nick == None:
              await self.schreibeNachricht(msg, f'Eine Nachricht von User {msg.author.name} wurde gelöscht.')
            else:
              await self.schreibeNachricht(msg, f'Eine Nachricht von User {msg.author.nick} wurde gelöscht.')

    async def testBefehl(self, msg):
        server = msg.guild
  
    async def Hilfe(self, msg):
        await self.schreibeNachricht(msg, '*Systemüberblick*  \n' +
        'Wert \n'+
        'Bewegen <Raum> \n'+
        'ZeigeStatus \n'+
        '<Station>Energie <Wert>\n'+
        '<Station>Anzeige \n'
        )
        
