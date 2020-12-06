import discord
import ast
import csv
import json

class Umgebung:  
    async def fehler(self, msg):
        await self.schreibeNachricht(msg, "Unbekanntes Kommando.")
        pass

    async def befehl(self, msg):
        eingaben = msg.content.split(' ')
        if eingaben[0] in dir(Umgebung):
            return await getattr(self, eingaben[0], lambda fehler: "unbekannt")(msg)
        else:
            await self.fehler(msg)

    def __init__(self):
        self.LadeStartWerte()
        print('Startwerte gelesen')
        print(self.Werte) 

    # Laed Werte aus einer gespeicherten Session
    def LadeWerte(self, datei):
        self.Werte = []
        with open(datei) as json_file:
            self.Werte = json.load(datei)
        
    def SchreibeWerte(self, datei):
        json.dump(self.Werte, datei)        

    # laed die CSV Datei mit den Startwerten 
    def LadeStartWerte(self, msg=None):
        self.Werte = []
        with open('Initialwerte.csv', 'r') as datei:
            reader = csv.reader(datei, delimiter = ',')
            self.Werte = {rows[0]:float(rows[1]) for rows in reader}
        self.Werte['Klick'] = 0

    #
    def parameter(self, msg, nr):
        eingaben = msg.content.split(' ')
        if len(eingaben)-1 < nr:
            return 'Fehler'
        else:
            return eingaben[nr].strip()

    # Wert mit Überprüfung setzen           
    async def setzeWert(self, msg, wertname, wert, pruefwertname=''):
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

    async def aendereWert(self, msg, bezeichnung):
        await self.setzeWert(msg, f'Energieverbrauch_{bezeichnung}', self.parameter(msg,1), f'Energieverbrauch_{bezeichnung}_max')

    async def Anzeige(self, msg, bezeichnung, text=None):
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

    async def AquaAnzeige(self, parameter):
        await self.schreibeNachricht(msg,f'Energieverbrauch Aquaristikmodul: ' +
                                       str(self.Werte['Energieverbrauch_Aqua']) +
                                       ' von '+
                                       str(self.Werte['Energieverbrauch_Aqua_max'])+
                                       '\n'+
                                       'Anteil Luft-/Nahrungserzeugung: '+
                                       str(float(self.Werte['Energieanteil_Aqua_Lufterzeugung'])*100) +
                                       '%'  )
  
    async def AquaEnergie(self, msg):
        await self.aendereWert(msg, 'Aqua')

    async def BioEnergie(self, msg):
        await self.aendereWert(msg, 'Bio')

    async def BioAnzeige(self, parameter):
        await self.schreibeNachricht(msg,f'Energieverbrauch Bioristikmodul: ' +
                                       str(self.Werte['Energieverbrauch_Bio']) +
                                       ' von '+
                                       str(self.Werte['Energieverbrauch_Bio_max'])+
                                       '\n'+
                                       'Anteil Luft-/Nahrungserzeugung: '+
                                       str(float(self.Werte['Energieanteil_Bio_Lufterzeugung'])*100) +
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
        await self.schreibeNachricht(msg,f'Klick ' + str(self.Werte['Klick']) + 
                ': Energie='+str(self.Werte['Energie'])+ 
                ' Brennstoff='+str(self.Werte['Brennstoff'])+
                ' Nahrung='+str(self.Werte['Nahrung'])+
                ' Luft='+str(self.Werte['Luft']))

    # Spiellogiken
    async def GeneratorStart(self, msg):
        self.Werte['Brennstoff'] -= self.Werte['Energieverbrauch_Generator']*(1-self.Werte['Techstufe_Ingenieur'])
        self.Werte['Energie'] += self.Werte['Energieverbrauch_Generator']*self.Werte['Generatorfaktor']*self.Werte['Techstufe_Ingenieur']-self.Werte['Energieverbrauch_Generator']

    async def RecyclingStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Recycling']*(1-self.Werte['Techstufe_Recycling'])
        self.Werte['Luft'] -= self.Werte['Energieverbrauch_Recycling']*(1-self.Werte['Techstufe_Recycling'])
        self.Werte['Brennstoff'] += self.Werte['Energieverbrauch_Recycling']*self.Werte['Brennstoff_Anpassungsfaktor']*self.Werte['Techstufe_Recycling']

    async def AquaStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Aqua']*(1-self.Werte['Techstufe_Facility'])
        self.Werte['Luft'] += self.Werte['Energieverbrauch_Aqua']*self.Werte['Energieanteil_Aqua_Lufterzeugung']*self.Werte['Techstufe_Aqua']*self.Werte['Lufterzeugung_Anpassungsfaktor']
        self.Werte['Nahrung'] += self.Werte['Energieverbrauch_Aqua']*(1-self.Werte['Energieanteil_Aqua_Lufterzeugung'])*self.Werte['Techstufe_Aqua']*self.Werte['Nahrungs_Anpassungsfaktor']

    async def BioStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Bio']*(1-self.Werte['Techstufe_Facility'])
        self.Werte['Luft'] += self.Werte['Energieverbrauch_Bio']*self.Werte['Energieanteil_Bio_Lufterzeugung']*self.Werte['Techstufe_Bio']*self.Werte['Lufterzeugung_Anpassungsfaktor']
        self.Werte['Nahrung'] += self.Werte['Energieverbrauch_Bio']*(1-self.Werte['Energieanteil_Bio_Lufterzeugung'])*self.Werte['Techstufe_Bio']*self.Werte['Nahrungs_Anpassungsfaktor']

    async def AussenhuelleStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Aussenhuelle']*(1-self.Werte['Techstufe_Technik'])

    async def ForschungsmodulStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Forschungsmodul']*(1-self.Werte['Techstufe_Ingenieur'])
              
    async def KrankenstationStart(self, msg):
        self.Werte['Energie'] += self.Werte['Energieverbrauch_Krankenstation']*self.Werte['Krankenstationfaktor']*self.Werte['Techstufe_Facility'] - self.Werte['Energieverbrauch_Krankenstation']
      
    async def LagerStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Lager']*self.Werte['Techstufe_Facility']

    async def MultiStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Multi']*(1-self.Werte['Techstufe_Facility'])                              

    async def KommandoStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Kommando']*(1-self.Werte['Techstufe_Facility'])        

    async def GeheimlaborStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Geheimlabor']*(1-self.Werte['Techstufe_Facility'])        

    async def MesseStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Messe']*(1-self.Werte['Techstufe_Facility'])        

    async def ServerraumStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Serverraum']*(1-self.Werte['Techstufe_Informatik'])        

    async def SolarStart(self, msg):
        self.Werte['Energie'] += self.Werte['Energieverbrauch_Solar']*self.Werte['Techstufe_Technik']*self.Werte['Solarfaktor'] - self.Werte['Energieverbrauch_Solar']      

    async def EnergiespeicherStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Energiespeicher']*(1-self.Werte['Techstufe_Facility'])        
        self.Werte['Energie_max'] = (self.Werte['Energiespeicher_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Energiespeicher_max']*0.2*self.Werte['Energieverbrauch_Energiespeicher'])

    async def KuehlmodulStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Kuehlmodul']*(1-self.Werte['Techstufe_Facility'])        
        self.Werte['Nahrung_max'] = (self.Werte['Nahrung_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Nahrung_max']*0.2*self.Werte['Energieverbrauch_Kuehlmodul'])

    async def LufttankStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Lufttank']*(1-self.Werte['Techstufe_Technik'])        
        self.Werte['Luft_max'] = (self.Werte['Lufttank_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Luft_max']*0.2*self.Werte['Energieverbrauch_Lufttank'])

    async def BrennstofflagerStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Brennstofflager']*(1-self.Werte['Techstufe_Technik'])        
        self.Werte['Nahrung_max'] = (self.Werte['Brennstoff_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Brennstoff_max']*0.2*self.Werte['Energieverbrauch_Brennstofflager'])

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
        await self.MesseStart(msg)
        await self.ServerraumStart(msg)
        await self.EnergiespeicherStart(msg)
        await self.KuehlmodulStart(msg)
        await self.LufttankStart(msg)
        await self.BrennstofflagerStart(msg)
        await self.SolarStart(msg)
        self.Werte['Nahrung'] -= self.Werte['Nahrungsverbrauch_proZyklus']
        self.Werte['Luft'] -= self.Werte['Luftverbrauch_Geheimlabor'] + self.Werte['Luftverbrauch_Module'] + self.Werte['Luftverbrauch_Recycling']
        self.Werte['Klick'] += 1
        await self.ZeigeStatus(msg)
        if (self.Werte['Energie'] < 0) or (self.Werte['Luft'] < 0) or (self.Werte['Nahrung'] < 0) or (self.Werte['Brennstoff'] < 0):
                 await self.schreibeNachricht(msg,f'Die Resourcen sind zuende gegangen!')

    async def Teilnehmen(self, msg):
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
                
            

    async def Bewegen(self, msg):
        server = msg.guild
        dest = discord.utils.find(lambda m: m.name.lower()==channel.lower() and channel.category=='Orte', server.voice_channels) 
        text = ''
        if dest is None:
            name = msg.author.name 
            category = discord.utils.find(lambda m: m.name=='Orte', server.categories)
            overwrites = {
                    msg.author: discord.PermissionOverwrite(connect=True, speak=True),
                    }
            dest = await server.create_voice_channel(channel, overwrites=overwrites, category=category)
            text = 'als erster '
        else:
            await dest.set_permissions(msg.author, connect=True, speak=True) 
       
        if msg.author.voice is not None:
          ch = msg.author.voice.channel
          if ch is not None: 
            await self.schreibeNachricht(msg, f'{msg.author.name} verlässt {msg.author.voice.channel} und betritt {text}{channel}')
            await ch.set_permissions(msg.author, connect=False,speak=False)
          else:
             await self.schreibeNachricht(msg, f'{msg.author.name} betritt {text}{channel} aus dem Nichts')
        else:
            await self.schreibeNachricht(msg, f'{msg.author.name} betritt {text}{channel} aus dem Nichts') 
        await msg.author.move_to(dest, reason='betritt den Raum')




    #Hilfsfunktionen für discord

    # Nachricht mit einem Bild, picture ist Filename 
    async def schreibeNachricht(self, msg, text, picture=None):
        if picture is None:
            await msg.channel.send(text)
        else:
            with open(picture, 'rb') as f:
               picture = discord.File(f)
               await msg.channel.send(msg.channel, picture)

    async def loggeLoeschen(self, msg):
        await self.schreibeNachricht(msg, f'User {msg.author} hat eine Nachricht gelöscht.')
        
    