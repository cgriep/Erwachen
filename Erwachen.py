import discord
import ast
import csv
import json
import sys
import pathlib
import datetime
import os
import os.path
from os import path

class Umgebung:
    client = None
    async def fehler(self, msg, text="Unbekanntes Kommando."):
        await self.schreibeNachricht(msg, f'*{text}*')
        await self.schreibeSystemnachricht(msg, f'*{text}*: {msg.author.nick} durch Kommando {msg.content}')

    async def befehl(self, msg):
        # nur in Spielchannels reagieren
        if msg.channel.name == self.Werte['Kanal_Start'] or msg.channel.name.startswith(self.Werte['Kanal_Konsole']):
            eingaben = msg.content.split(' ')
            if msg.channel.name == 'start-portal' and eingaben[0] != 'Teilnehmen':
                return
            if '?' in msg.content:
              await self.schreibeNachricht(msg,'*Ask for system help if needed*') 
              return
            if eingaben[0] == '#':
                return            
            if eingaben[0] in dir(Umgebung):
              if await self.Berechtigung(msg):
                return await getattr(self, eingaben[0], lambda fehler: "unbekannt")(msg)
            else:
              for answer in self.Werte:
                if answer.startswith('Answer_'):
                  text = answer[7:]                  
                  if text.lower() in msg.content.lower():
                    await self.schreibeNachricht(msg,self.Werte[answer]) 
                    return
              # wurde ein Spielername verwendet ?
              for name in eingaben:
                dest = discord.utils.find(lambda m: m.name.endswith('-'+name) and m.category.name==self.Werte['Kategorie_Konsole'], msg.guild.text_channels)
                if dest is not None:
                  await self.schreibeNachricht(msg, name+' per Lokalisierung finden oder über Konsole ansprechen.')
                  return
              await self.fehler(msg)            
        else:
            print('Channel '+msg.channel.name+' ignoriert')

    def __init__(self):
        pass

    # Laed Werte aus einer gespeicherten Session
    async def LadeWerte(self, msg, init=False):
        self.Werte = []
        name = self.parameter(msg, 1)
        if name == 'Fehler' and not init:
          await self.LadeStartWerte(msg)
          return
        else:
          name = 'Erwachen'
        try:          
          with open('save/'+name+'.sav', 'r') as json_file:
              self.Werte = json.load(json_file)
          if msg is not None: 
            fname = pathlib.Path(name+'.sav')
            await self.schreibeSystemnachricht(msg, f'Werte aus {name} wurden geladen.\n' + 
              'Systemstand Klick '+str(self.Werte['Klick'])+' vom '+str(datetime.datetime.fromtimestamp(fname.stat().st_mtime)))
        except:
          if msg is not None:
            await self.schreibeSystemnachricht(msg, f'Laden fehlgeschlagen: {msg.content}')    

    async def SchreibeWerte(self, msg, name=None):
        if name is None:
          name = self.parameter(msg, 1)
        if not path.exists('save'):
            os.mkdir('save')  
        with open('save/'+name+'.sav', 'w') as json_file:
            json.dump(self.Werte, json_file)
        await self.schreibeSystemnachricht(msg, f'Werte wurden als {name} gesichert.')

    # laed die CSV Datei mit den Startwerten
    async def LadeStartWerte(self, msg=None):
        self.Werte = []
        with open('Initialwerte.csv', 'r') as datei:
            reader = csv.reader(datei, delimiter = ',')
            self.Werte = {rows[0]:rows[1] for rows in reader}
        for wert in list(self.Werte):
          try:     
            self.Werte[wert] = float(self.Werte[wert])
          except: 
            # Textwerte, keine Aktion
            pass
        self.Werte['Klick'] = 0
        if msg is not None:
          await self.schreibeSystemnachricht(msg, 'Startwerte geladen.')
        else:
          if path.exists('save/Erwachen.sav'):
            await self.LadeWerte(msg, True)
            print('Gespeichertes Spiel geladen.')
          else:
            print('Startwerte gelesen')
          print(self.Werte)
          print ('Setze mit Klick '+str(self.Werte['Klick'])+' fort.')
        
    #
    def parameter(self, msg, nr=9999):
        try:
          eingaben = msg.content.split(' ')
          if len(eingaben)-1 < nr:
              return 'Fehler'
          else:
              return eingaben[nr].strip()
        except:
          return 'Fehler'

    # Wert mit Überprüfung setzen
    async def setzeWert(self, msg, wertname=None, wert='', pruefwertname='', div=1, num=True):
        if num:
          if not wert.isnumeric():
              await self.schreibeNachricht(msg,f'Der Wert "{wert}" ist ungültig. Kommando nicht ausführbar.')
              return(False)
          #Übertragen in Berechtigung
          #ch = self.getOrtChannel(msg).name
          #if wertname.find('_'+ch) == -1:   
          #     await self.schreibeNachricht(msg, '*System Error* Zu weit entfernt')
          #     await self.schreibeSystemnachricht(msg, f'Manipulationsversuch von {msg.author.nick} auf {wertname} von ausserhalb') 
          #     return
          wert = float(wert)/div
          pruefwert = 9999
          if not pruefwertname.isnumeric():
            if pruefwertname != '':
              pruefwert = self.Werte[pruefwertname]
          else:
            pruefwert = pruefwertname
          if (wert > pruefwert) or (wert < 0):
                  await self.schreibeNachricht(msg,f'Der Wert {wert} ist nicht erlaubt. Kommando nicht ausführbar.')
                  return(False)
        self.Werte[wertname] = wert
        await self.schreibeNachricht(msg,f'Der Wert {wert} wurde gesetzt. ')
        await self.schreibeSystemnachricht(msg, f'{wertname} geändert von {msg.author.nick} in {self.getOrtChannel(msg)} auf {wert}')
        return(True)

    async def Wert(self, msg):
        par = self.parameter(msg, 2)
        name = self.parameter(msg, 1)
        try:
            if par == 'Fehler':
                await self.schreibeNachricht(msg,name+'= '+str(self.Werte[name]))
            else:
                await self.setzeWert(msg=msg, wertname=name, wert=par, num=par.isnumeric())
        except:
            await self.fehler(msg)

    async def aendereWert(self, msg, bezeichnung=None, Art='Energieverbrauch', div=1):
        await self.setzeWert(msg, f'{Art}_{bezeichnung}', self.parameter(msg,1), f'{Art}_{bezeichnung}_max', div)

    async def Energie(self, msg):
        await self.setzeWert(msg, f'Energieverbrauch_'+self.parameter(msg, 1), self.parameter(msg, 2), f'Energieverbrauch_'+self.parameter(msg, 1)+'_max')

    async def Anzeige(self, msg, bezeichnung=None, text=None, add=None):
        if bezeichnung is None:
          bezeichnung = self.parameter(msg, 1) 
        if bezeichnung == 'Fehler':
          await self.schreibeNachricht(msg, 'Unbekannter Befehl.')
          return
        # prüfe ob eine Übersetzung vorhanden ist 
        try:
            text = self.Werte['Text_'+bezeichnung]
        except:
            text = bezeichnung
        if bezeichnung == 'Status':
          await self.AnzeigeStatus(msg)
          return
        try:
          #Übertragen in Berechtigung
          #ch = self.getOrtChannel(msg).name
          #if ch == bezeichnung or ch == text:                
          text = f'{text}energie ist eingestellt auf ' + str(self.Werte[f'Energieverbrauch_{bezeichnung}'] ) + ' von ' + str(self.Werte[f'Energieverbrauch_{bezeichnung}_max'])
          if add is not None:
              text += '\n' + add
          await self.schreibeNachricht(msg,text)
          await self.schreibeSystemnachricht(msg, f'{text} von {msg.author.nick} in {self.getOrtChannel(msg)} angezeigt')
          #else:
          #  await self.schreibeNachricht(msg, '*System Error* Zu weit entfernt.')
          #  await self.schreibeSystemnachricht(msg, f'Zugriffsversuch von {msg.author.nick} auf {bezeichnung} aus {ch}') 
        except:
          await self.schreibeNachricht(msg, '***Critical System Error***')
          await self.schreibeSystemnachricht(msg, f'Zugriffsversuch von {msg.author.nick} auf {bezeichnung} von ausserhalb') 

    async def ModulSchalten(self, msg):
        # umschalten eines Moduls. 
        modul = self.parameter(msg, 1)
        override = self.parameter(msg, 2)
        if modul == 'Fehler':
          await self.schreibeNachricht(msg, 'Unbekannter Befehl')
          return
        try:
          ch = self.getOrtChannel(msg).name
          #if ch != modul:
          #  await self.schreibeNachricht(msg, '*System Error* Zu weit entfernt.')
          #  await self.schreibeSystemnachricht(msg, f'Schaltversuch von {msg.author.nick} auf {modul} aus {ch}') 
          #  return
          if self.Werte['Modul_'+modul] == 1:
            # ausschalten
            dest = discord.utils.find(lambda m: m.name==modul and m.category.name==self.Werte['Kategorie_Orte'], msg.guild.voice_channels)
            if dest is not None:
              if override == 'Fehler' and (len(dest.members) > 0):
                await self.schreibeNachricht(msg, 'Es befinden sich noch Personen im Modul. Override notwendig.')
                return
            self.Werte['Modul_'+modul] = 0
            text = ''
            if override == '!':
              text = 'zwangsweise '
            await self.schreibeNachricht(msg, f'Modul {modul} {text}abgeschaltet.')            
            await self.schreibeSystemnachricht(msg, f'Modul {modul} von {msg.author.nick} {text}ausgeschaltet.')
            # Luft ablassen  
            if len(dest.members) > 0:
              await self.Ton(msg, modul, self.Werte['Hinweis_Druckabfall'])
          else:
            # einschalten
            await self.schreibeNachricht(msg, f'Modul {modul} eingeschaltet.')
            await self.schreibeSystemnachricht(msg, f'Modul {modul} von {msg.author.nick} eingeschaltet.')
            self.Werte['Modul_'+modul] = 1
        except:
          await self.schreibeNachricht(msg, '***Critical System Error***')
          await self.schreibeSystemnachricht(msg, f'Schaltversuch von {msg.author.nick} auf {modul} von ausserhalb') 

    async def Modul(self, msg):
      # info über das Modul
      try:
        ch = self.getOrtChannel(msg).name
      except:
        await self.schreibeNachricht(msg, '***Critical System Error***')
        await self.schreibeSystemnachricht(msg, f'Modulzugriff von {msg.author.nick} von ausserhalb') 
        return
      try:
        text = self.Werte['Modultext_'+ch]
        await self.schreibeNachricht(msg, f'*Information:*\n{text}')
      except:
        await self.schreibeNachricht(msg, '*Internal error*: No description available')
        await self.schreibeSystemnachricht(msg, f'*Fehler*: Keine Beschreibung für Modul {ch}') 
      

    # Spielbefehle Anzeige / Wertänderung
    async def GeneratorraumEnergie(self, msg):
        await self.aendereWert(msg, 'Generatorraum')

    async def GeneratorraumAnzeige(self, msg):
        await self.Anzeige(msg, 'Generatorraum')

    async def RecyclingraumAnzeige(self, msg):
        await self.Anzeige(msg, 'Recyclingraum')

    async def RecyclingraumEnergie(self, msg):
        await self.aendereWert(msg, 'Recyclingraum')

    async def AquatoriumAnzeige(self, msg):
        await self.Anzeige(msg, 'Aquatorium', 'Aquatorium', 'Anteil Luft-/Nahrungserzeugung: ' +
                                       str(float(self.Werte['Energieanteil_Aquatorium_Lufterzeugung']) * 100) +
                                       '%' )

    async def AquatoriumEnergie(self, msg):
        await self.aendereWert(msg, 'Aquatorium')

    async def AquatoriumVerhaeltnis(self, msg):
        await self.aendereWert(msg, 'Aquatorium_Lufterzeugung', 'Energieanteil',100)


    async def BiotopVerhaeltnis(self, msg):
        await self.aendereWert(msg, 'Bio_Lufterzeugung', 'Energieanteil',100)

    async def BiotopEnergie(self, msg):
        await self.aendereWert(msg, 'Biotop')   

    async def BiotopAnzeige(self, msg):
        await self.Anzeige(msg, 'Biotop', 'Biotopmodul', 'Anteil Luft-/Nahrungserzeugung: ' +
                                       str(float(self.Werte['Energieanteil_Biotop_Lufterzeugung']) * 100) +
                                       '%'  )

    async def AussenhuelleEnergie(self, msg):
        await self.aendereWert(msg, 'Aussenhuelle')

    async def AussenhuelleAnzeige(self, msg):
        await self.Anzeige(msg, 'Aussenhuelle')

    async def LufttankEnergie(self, msg):
        await self.aendereWert(msg, 'Lufttank')

    async def LufttankAnzeige(self, msg):
        await self.Anzeige(msg, 'Lufttank')

    async def KuehlhausEnergie(self, msg):
        await self.aendereWert(msg,'Kuehlhaus')

    async def KuehlhausAnzeige(self, msg):
        await self.Anzeige(msg,'Kuehlhaus')

    async def ServerraumEnergie(self, msg):
        await self.aendereWert(msg,'Serverraum')

    async def ServerraumAnzeige(self, msg):
        await self.Anzeige(msg,'Serverraum')

    async def KrankenstationEnergie(self, msg):
        await self.aendereWert(msg,'Krankenstation')

    async def KrankenstationAnzeige(self, msg):
        await self.Anzeige(msg,'Krankenstation')

    async def LagerraumEnergie(self, msg):
        await self.aendereWert(msg,'Lagerraum')

    async def LagerraumAnzeige(self, msg):
        await self.Anzeige(msg,'Lagerraum')

    async def MultifunktionEnergie(self, msg):
        await self.aendereWert(msg,'Multifunktion')

    async def MultifunktionAnzeige(self, msg):
        await self.Anzeige(msg,'Multifunktion')

    async def KommandoraumEnergie(self, msg):
        await self.aendereWert(msg,'Kommandoraum')

    async def KommandoraumAnzeige(self, msg):
        await self.Anzeige(msg,'Kommandoraum')

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

    async def ForschungslaborEnergie(self, msg):
        await self.aendereWert(msg,'Forschungslabor')

    async def ForschungslaborAnzeige(self, msg):
        await self.Anzeige(msg,'Forschungslabor')

    async def SolarsteuerungEnergie(self, msg):
        await self.aendereWert(msg,'Solarsteuerung')

    async def SolarsteuerungAnzeige(self, msg):
        await self.Anzeige(msg,'Solarsteuerung')

    async def AnzeigeStatus(self, msg):
        text = f' ***System-Status*** || *Klick ' + str(self.Werte['Klick']) + '* \n' \
                'Energie      = '+ str(self.Werte['Energie']) + ' von maximal: ' + str(self.Werte['Energie_max']) + ' \n'  \
                'Brennstoff = ' + str(self.Werte['Brennstoff']) + ' von maximal: ' + str(self.Werte['Brennstoff_max']) + ' \n' \
                'Nahrung     = ' + str(self.Werte['Nahrung']) + ' von maximal: ' + str(self.Werte['Nahrung_max']) + ' \n' \
                'Luft             = ' + str(self.Werte['Luft']) + ' von maximal: ' + str(self.Werte['Luft_max']) 
        await self.schreibeNachricht(msg, text)
        return text 

    # Spiellogiken
    async def AquatoriumStart(self, msg):
        self.Werte['Energie']    -= self.Werte['Energieverbrauch_Aquatorium'] * (2-self.Werte['Techstufe_Facility'])
        self.Werte['Luft']       += self.Werte['Energieverbrauch_Aquatorium'] * self.Werte['Energieanteil_Aquatorium_Lufterzeugung'] * self.Werte['Techstufe_Aquatorium'] * self.Werte['Lufterzeugung_Anpassungsfaktor']
        self.Werte['Nahrung']    += self.Werte['Energieverbrauch_Aquatorium'] * (1-self.Werte['Energieanteil_Aquatorium_Lufterzeugung'])*self.Werte['Techstufe_Aquatorium']*self.Werte['Nahrungs_Anpassungsfaktor']
        self.Werte['Brennstoff'] -= self.Werte['Energieverbrauch_Aquatorium'] * (2-self.Werte['Techstufe_Recyclingraum'])


    async def AussenhuelleStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Aussenhuelle']*(2-self.Werte['Techstufe_Technik'])


    async def BiotopStart(self, msg):
        self.Werte['Energie']       -= self.Werte['Energieverbrauch_Biotop'] * (2-self.Werte['Techstufe_Facility'])
        self.Werte['Luft']          += self.Werte['Energieverbrauch_Biotop'] * self.Werte['Energieanteil_Biotop_Lufterzeugung'] * self.Werte['Techstufe_Biotop'] * self.Werte['Lufterzeugung_Anpassungsfaktor']
        self.Werte['Nahrung']       += self.Werte['Energieverbrauch_Biotop'] * (1-self.Werte['Energieanteil_Biotop_Lufterzeugung'])*self.Werte['Techstufe_Biotop']*self.Werte['Nahrungs_Anpassungsfaktor']
        self.Werte['Brennstoff']    -= self.Werte['Energieverbrauch_Biotop'] * (2-self.Werte['Techstufe_Recyclingraum'])

    async def StartModul(self, msg):
        modul = self.parameter(msg, 1)
        if modul == 'Forschungslabor':
          self.Werte['Energie'] -= self.Werte['Energieverbrauch_Forschungslabor']*(2-self.Werte['Techstufe_Ingenieur'])

    async def ForschungslaborStart(self, msg):
        msg.content = 'StartModul Forschungslabor'
        await self.StartModul(msg)

    async def GeheimlaborStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Geheimlabor']*(2-self.Werte['Techstufe_Kollaborateur'])

    async def GeheimlagerStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Geheimlager']*(2-self.Werte['Techstufe_Kollaborateur'])

    async def GeneratorraumStart(self, msg):
        self.Werte['Brennstoff'] -= self.Werte['Energieverbrauch_Generatorraum']*(2-self.Werte['Techstufe_Ingenieur'])
        self.Werte['Energie']    += self.Werte['Energieverbrauch_Generatorraum']*self.Werte['Generatorraumfaktor']*self.Werte['Techstufe_Ingenieur']-self.Werte['Energieverbrauch_Generatorraum']

    async def MesseStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Messe']*(2-self.Werte['Techstufe_Facility'])

    async def KommandoraumStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Kommandoraum']*(2-self.Werte['Techstufe_Facility'])

    async def KrankenstationStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Krankenstation']*self.Werte['Krankenstationfaktor'] - self.Werte['Energieverbrauch_Krankenstation']*self.Werte['Techstufe_Facility']

    async def LagerraumStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Lagerraum']*(2-self.Werte['Techstufe_Facility'])

    async def MultifunktionStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Multifunktion']*(2-self.Werte['Techstufe_Facility'])

    async def ServerraumStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Serverraum']*(2-self.Werte['Techstufe_Informatik'])

    async def SolarsteuerungStart(self, msg):
        self.Werte['Energie'] += self.Werte['Energieverbrauch_Solarsteuerung']*self.Werte['Techstufe_Technik']*self.Werte['Solarsteuerungfaktor'] - self.Werte['Energieverbrauch_Solarsteuerung']

    async def RecyclingraumStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Recyclingraum']*(2-self.Werte['Techstufe_Recyclingraum'])
        self.Werte['Luft'] -= self.Werte['Energieverbrauch_Recyclingraum']*(2-self.Werte['Techstufe_Recyclingraum'])
        self.Werte['Brennstoff'] += self.Werte['Energieverbrauch_Recyclingraum']*self.Werte['Brennstoff_Anpassungsfaktor']*self.Werte['Techstufe_Recyclingraum']


    # Lager/ Systemwerte

    async def EnergiespeicherStart(self, msg):
        self.Werte['Energie']    -= self.Werte['Energieverbrauch_Energiespeicher']*(2-self.Werte['Techstufe_Facility']) + self.Werte['Energieverbrauch_Verluste']
        self.Werte['Energie_max'] = (self.Werte['Energiespeicher_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Energiespeicher_max']*0.2*self.Werte['Energieverbrauch_Energiespeicher'])

    async def KuehlhausStart(self, msg):
        self.Werte['Energie']    -= self.Werte['Energieverbrauch_Kuehlhaus']*(2-self.Werte['Techstufe_Facility'])
        self.Werte['Nahrung_max'] = (self.Werte['Nahrungsspeicher_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Nahrungsspeicher_max']*0.2*self.Werte['Energieverbrauch_Kuehlhaus'])
        self.Werte['Nahrung']    -= self.Werte['Nahrungsverbrauch_proZyklus']

    async def LufttankStart(self, msg):
        self.Werte['Energie'] -= self.Werte['Energieverbrauch_Lufttank']*(2-self.Werte['Techstufe_Technik'])
        self.Werte['Luft_max'] = (self.Werte['Lufttank_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Lufttank_max']*0.2*self.Werte['Energieverbrauch_Lufttank'])
        self.Werte['Luft']    -= self.Werte['Luftverbrauch_Geheimlabor'] + self.Werte['Luftverbrauch_Module'] 

    async def BrennstofflagerStart(self, msg):
        self.Werte['Energie']       -= self.Werte['Energieverbrauch_Brennstofflager']*(2-self.Werte['Techstufe_Technik'])
        self.Werte['Brennstoff_max'] = (self.Werte['Brennstoff_tankvolumen_max']*self.Werte['Techstufe_Technik']) + (self.Werte['Brennstoff_tankvolumen_max']*0.2*self.Werte['Energieverbrauch_Brennstofflager'])

    async def ZugEnde(self, msg):
        await self.schreibeSystemnachricht(msg, '**Processing commands**\nBeende Klick ' + str(self.Werte['Klick']))
        await self.GeneratorraumStart(msg)
        await self.BiotopStart(msg)
        await self.AquatoriumStart(msg)
        await self.RecyclingraumStart(msg)
        await self.AussenhuelleStart(msg)
        await self.ForschungslaborStart(msg)
        await self.KrankenstationStart(msg)
        await self.LagerraumStart(msg)
        await self.MultifunktionStart(msg)
        await self.KommandoraumStart(msg)
        await self.GeheimlaborStart(msg)
        await self.GeheimlagerStart(msg)

        await self.MesseStart(msg)
        await self.ServerraumStart(msg)
        await self.EnergiespeicherStart(msg)
        await self.KuehlhausStart(msg)
        await self.LufttankStart(msg)
        await self.BrennstofflagerStart(msg)
        await self.SolarsteuerungStart(msg)

        self.Werte['Klick'] += 1
        text = await self.AnzeigeStatus(msg)
        await self.schreibeSystemnachricht(msg, text)
        if (self.Werte['Energie'] < 0) or (self.Werte['Luft'] < 0) or (self.Werte['Nahrung'] < 0) or (self.Werte['Brennstoff'] < 0):
                 await self.schreibeSystemnachricht(msg, '***Die Resourcen sind zuende gegangen!***')

    async def Teilnehmen(self, msg):
        if msg.channel.name != self.Werte['Kanal_Start']:
            await self.schreibeNachricht(msg,'***System Error*** Erwachung ohne Schlaf')
            return
        name = self.parameter(msg, 1).strip().lower()
 
        # prüfen ob User bereits im Spiel ist 
        for channel in msg.guild.text_channels:
          if channel.name != self.Werte['Kanal_Start'] and channel.category.name == self.Werte['Kategorie_Konsole'] and channel.name.startswith(self.Werte['Kanal_Konsole']):
            perm = channel.overwrites_for(msg.author)
            if perm.send_messages or perm.read_messages:
              await self.schreibeNachricht(msg, f'{channel.name} bereits vorhanden, bitte dort weiterspielen.')
              await self.schreibeSystemnachricht(msg,f'Versuch der Persönlichkeitsspaltung durch {msg.author} mit Name {name}')
              return
        # prüfen ob channel schon da ist
 
        # channel erzeugen
        channel = discord.utils.get(msg.guild.text_channels, name=self.Werte['Kanal_Konsole']+name)
        if channel is not None:
            await self.schreibeNachricht(msg, 'Zugriff für diesen Namen verweigert. Wähle einen anderen.')
        else:
            category = discord.utils.find(lambda m: m.name==self.Werte['Kategorie_Konsole'], msg.guild.categories)
            overwrites = {
                    msg.author: discord.PermissionOverwrite(send_messages=True, read_messages=True),
                    msg.guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=False),
                    msg.guild.me: discord.PermissionOverwrite(send_messages=True, read_messages=True)
                    }
            dest = await msg.guild.create_text_channel(self.Werte['Kanal_Konsole']+name, overwrites=overwrites, category=category)
            await dest.send(f'Willkommen {name}. Wünsche wohl geruht zu haben.')
            # nickname ändern - funktioniert nur bei normalen Benutzern, nicht bei Admins!
            try:
                await msg.author.edit(nick = name)
                await dest.send(f'Nickname wurde geändert.')
            except:
                await self.schreibeNachricht(msg, f'Nickname des priviligierten Accounts konnte nicht geändert werden.')
            perms = msg.channel.overwrites_for(msg.author)
            perms.send_messages=False
            perms.read_messages=False
            await msg.channel.set_permissions(msg.author, overwrite=perms, reason="Teilnehmen-Command")
            # entferne die Teilnahme-Nachricht
            await msg.delete()
            await self.schreibeSystemnachricht(msg, f'{msg.author.name} betritt als {msg.author.nick} das System')
            # Spieler für Aufwachraum berechtigen 
            dest = discord.utils.find(lambda m: m.name=='Aufwachraum' and m.category.name==self.Werte['Kategorie_Orte'], server.voice_channels)
            if dest is not None:
              perms = dest.overwrites_for(msg.author)
              perms.connect=True
              perms.speak=True
              perms.view_channel=True
              await dest.set_permissions(msg.author, overwrite=perms, reason="Teilnehmen-Command")
              # Spieler in den Aufwachraum bewegen
              try:
                ch = msg.author.voice.channel
                if ch is not None:
                  await msg.author.move_to(dest, reason='betritt das Spiel')
              except:
                await self.schreibeNachricht(msg, 'Keine Sprachverbindung gefunden. Bitte manuell verbinden.')             
            # prüfen ob Aufwachraum aktiviert ist!
            if self.Werte['Modul_Aufwachraum'] == 0:
              self.Werte['Modul_Aufwachraum'] = 1
              await self.Systemnachricht(msg,'Aufwachraum wurde aktiviert.')
              
    async def Bewegen(self, msg):
        try:
          ch = msg.author.voice.channel
          if ch is None:
            raise ValueError('Kein Sprachkanal vorhanden.')
        except:
             await self.schreibeNachricht(msg, 'Bewegen ohne Sprachverbindung ist nicht möglich. Bitte erst verbinden.')
             return
        if ch.category.name != self.Werte['Kategorie_Orte']:
            await self.schreibeNachricht(msg,' Bewegen nur mit Sprachverbindung in einem Modul möglich.')
            return
        server = msg.guild
        channel = self.parameter(msg, 1).strip()
        if channel == ch.name:
            await self.schreibeNachricht(msg,' Modul ist bereits erreicht.')
            return
    
        # Bewegung nur in bekannte und aktivierte Module
        try:
            if self.Werte['Modul_'+channel] == 1:
                dest = discord.utils.find(lambda m: m.name==channel and m.category.name==self.Werte['Kategorie_Orte'], server.voice_channels)
                text = ''
                overwrites = {
                            msg.author: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
                            }
                if dest is None:
                    name = msg.author.nick
                    category = discord.utils.find(lambda m: m.name==self.Werte['Kategorie_Orte'], server.categories)
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
                      if ch.category.name==self.Werte['Kategorie_Orte']:
                        await self.schreibeNachricht(msg, f'{msg.author.nick} verlässt {msg.author.voice.channel} und betritt {text}{channel}')
                        perms = msg.author.voice.channel.overwrites_for(msg.author)
                        perms.connect=False
                        perms.speak=False
                        perms.view_channel=False
                        await msg.author.voice.channel.set_permissions(msg.author, overwrite=perms, reason="Bewegen-Command")
                        await self.schreibeSystemnachricht(msg, f'{msg.author.nick} verlässt {msg.author.voice.channel} und betritt {text}{channel}')
                      else:
                        await self.schreibeNachricht(msg, f'{msg.author.nick} betritt {text}{channel} von ausserhalb kommend')
                    else:
                      await self.schreibeNachricht(msg, f'{msg.author.nick} betritt {text}{channel}, ist aber nicht verbunden')
                      
                  else:
                      await self.schreibeNachricht(msg, f'{msg.author.nick} betritt {text}{channel} ohne Sprachverbindung.')
                      return True
                except:
                  await self.schreibeNachricht(msg, 'Fehler beim Sprachkanal')
                await msg.author.move_to(dest, reason='betritt das Modul')
                if len(dest.members) > 3:
                  await self.schreibeNachricht(msg, 'Überfüllung! Luftqualität prüfen.')
                  await self.schreibeSystemnachricht(msg, f'*Critical* Überfüllung in {dest.name}: {len(dest.members)}')
            else:
                await self.schreibeNachricht(msg, 'Modul unbekannt oder deaktiviert.')
        except KeyError:
            await self.schreibeNachricht(msg,'Unbekanntes Modul')

    async def Konsole(self, msg):
        name = self.parameter(msg, 1)
        text = self.parameter(msg, 2)
        if text == 'Fehler':
          await self.schreibeNachricht(msg, '*Error*: Nichts zu übermitteln.')
          return
        if name != 'Fehler': 
            channel = discord.utils.get(msg.guild.text_channels, name=self.Werte['Kanal_Konsole']+name)
            if channel is None:
              await self.schreibeNachricht(msg, 'Unbekannte Konsole')
              return
            text = msg.content[(len(name)+1+7+1):]
            await channel.send(f'***Konsolennachricht:***\n{text}')
            await self.schreibeNachricht(msg, f'Nachricht an Konsole von {name} übermittelt.')
            await self.schreibeSystemnachricht(msg, f'Text an Konsole {name} durch {msg.author.nick}: {text}')
        else:
            await self.schreibeNachricht(msg, 'Unbekannte Konsole')

    async def KonsoleLog(self, msg):
        name = self.parameter(msg, 1)
        anz = self.parameter(msg, 2)
        if not anz.isnumeric():
          anz = 2
        else:
          anz = int(anz)
        if name != 'Fehler':
            channel = discord.utils.get(msg.guild.text_channels, name=self.Werte['Kanal_Konsole']+name)
            if channel is None:
              await self.schreibeNachricht(msg, 'Unbekannte Konsole')
              return
            text = f'***Konsolenlog {name}: ***\n'
            async for message in channel.history(limit=anz):
              text += message.content + '\n'             
            await self.schreibeNachricht(msg,text)
        else:
            await self.schreibeNachricht(msg, 'Unbekannte Konsole')
        await self.schreibeSystemnachricht(msg, f'Log von Konsole {name} Anz={anz} durch {msg.author.nick}')

    async def Postenreset(self, msg):
        for w in self.Werte:
          if w.startswith('Rolle_') and w != 'Rolle_System':
            if self.Werte[w] != 'Nicht vergeben':
              self.Werte[w] = 'Nicht verbeben, zuletzt '+self.Werte[w]
        await self.schreibeNachricht(msg, 'Posten wurden neu initialisiert.')
        await self.schreibeSystemnachricht(msg, f'Postenreset durch {msg.author.nick}')

    async def Posten(self, msg):
        name = self.parameter(msg, 1)
        art = self.parameter(msg, 2)
        try:
          if art == '-':
            if self.Werte['Rolle_'+name] != msg.author.nick:
              await self.schreibeNachricht(msg, 'Posten {name} nicht zugeordnet.')
            else:
              self.Werte['Rolle_'+name] = f'Nicht vergeben, zuletzt {msg.author.nick}'
              await self.schreibeNachricht(msg, f'Posten {name} abgelegt.')
              await self.schreibeSystemnachricht(msg, f'{msg.author.nick} hat Posten {name} abgelegt.')
          if art == '+':
            if self.Werte['Rolle_'+name].startswith('Nicht vergeben'):
              self.Werte['Rolle_'+name] = msg.author.nick
              await self.schreibeNachricht(msg, f'Posten {name} angenommen.')
              await self.schreibeSystemnachricht(msg, f'{msg.author.nick} hat Posten {name} angenommen.')
            else:
              await self.schreibeNachricht(msg, f'Posten {name} bereits an '+self.Werte['Rolle_'+name]+' vergeben.')
          if art != '+' and art != '-':
            await self.schreibeNachricht(msg, f'Posten {name}: '+self.Werte['Rolle_'+name])
        except:
          await self.fehler(msg)

    async def Lokalisierung(self, msg):
       erg = '***Modulbevölkerung***\n'
       for ch in msg.guild.voice_channels:
         if ch.category.name == self.Werte['Kategorie_Orte']:
           erg += '*'+ch.name+'*:\n'
           text = ''
           for m in ch.members:
             text += m.nick+'\n'
           if text == '':
             text = 'Niemand anwesend\n'
           erg += text
       await self.schreibeNachricht(msg, erg)
       await self.schreibeSystemnachricht(msg, f'Lokalisierung durch {msg.author.nick}\n{erg}')
      

    #Hilfsfunktionen für discord

    # Nachricht mit einem Bild, picture ist Filename
    async def schreibeNachricht(self, msg, text=None, picture=None):
        if picture is None:
            await msg.channel.send(text)
        else:
            with open(picture, 'rb') as f:
               picture = discord.File(f)
               await msg.channel.send(msg.channel, picture)

    async def schreibeSystemnachricht(self, msg, text=None):
        if text is None:
          return
        # vermeiden dass Nachrichten auf der Systemkonsole doppelt kommentiert werden
        if msg.channel.name == self.Werte['Kanal_Konsole']+self.Werte['Kanal_System']:
          return
        channel = discord.utils.get(msg.guild.text_channels, name=self.Werte['Kanal_Konsole']+self.Werte['Kanal_System'])
        if channel is None:
            category = discord.utils.find(lambda m: m.name==self.Werte['Kategorie_Konsole'], msg.guild.categories)
            overwrites = {
                    msg.guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=False),
                    msg.guild.me: discord.PermissionOverwrite(send_messages=True, read_messages=True)
                    }
            channel = await msg.guild.create_text_channel(self.Werte['Kanal_Konsole']+self.Werte['Kanal_System'], overwrites=overwrites, category=category)
            await channel.send('***Systeminitialisierung*** Bootvorgang erfolgreich.')
        await channel.send(text)

    async def loggeLoeschen(self, msg, channel=None):
        if msg is not None:
          if msg.channel.name.startswith(self.Werte['Kanal_Konsole']):
            if msg.author.nick == None:
              #await self.schreibeNachricht(msg, f'Eine Nachricht von User {msg.author.name} wurde gelöscht.')
              await self.schreibeSystemnachricht(msg, f'Eine Nachricht von User {msg.author.name} wurde in {msg.channel.name} gelöscht.')
            else:
              #await self.schreibeNachricht(msg, f'Eine Nachricht von User {msg.author.nick} wurde gelöscht.')
              await self.schreibeSystemnachricht(msg, f'Eine Nachricht von User {msg.author.name} wurde in {msg.channel.name} gelöscht.')
        else:
          if channel.name.startswith(self.Werte['Kanal_Konsole']):
            syschannel = discord.utils.get(channel.guild.text_channels, name=self.Werte['Kanal_Konsole']+self.Werte['Kanal_System'])
            await syschannel.send(f'Eine ältere Nachricht in {channel.name} wurde gelöscht.')

    def getOrtChannel(self, msg):
        try:
            if msg.author.voice is not None:
                ch = msg.author.voice.channel
                if ch.category.name==self.Werte['Kategorie_Orte']:
                    return ch
            return None
        except:
            return None

    async def Hinweis(self, msg):
      channel = self.parameter(msg, 1)
      art = self.parameter(msg, 2)
      try:
        ton = self.Werte['Hinweis_'+art]
        await self.schreibeSystemnachricht(msg, f'Hinweis in {channel}: {art}')
        await self.Ton(msg, channel, ton)
      except:
        await self.schreibeNachricht(msg, '*Critical Error* Hinweis nicht bekannt.')

    async def Alarm(self, msg):
      channel = self.parameter(msg, 1)
      await self.schreibeSystemnachricht(msg, f'Alarm in {channel}')
      await self.Ton(msg, self.parameter(msg, 1), self.Werte['Hinweis_Alarm'])

    async def Hilfe(self, msg):
        text = 'Wert <Wertname> [Wert] - Wert anzeigen oder setzen\n' 
        text += 'ZugEnde - nächsten Zug einleiten\n'
        text += 'Shutdown - Speichern und Bot beenden\n'
        text += 'LadeWerte [<file>] (ohne Parameter werden die Initialwerte geladen)\n'
        text += 'SchreibeWerte <file> (Achtung: Überschreibt ohne Warnung)\n' 
        text += '<Modul>Start - einzelnes Modul berechnen\n'
        text += 'Alarm <Modul>\n'
        text += 'Hinweisliste - Hinweise für Module auflisten\n'
        text += 'Hinweis <Modul> <Art> - Hinweis in Modul abspielen\n'
        text += 'Systemnachrichten - Liste vorhandener Standardnachrichten\n'
        text += 'Systemnachricht <Text|Textname> - Sendet einen Text oder Standardtext an alle Konsolen\n' 
        text += 'Berechtigungen - Listet alle Berechtigungen auf\n'
        text += 'Berechtigung <befehl> <modul> <rolle> - Prüft die Berechtigung für eine Rolle in einem Modul\n'
        if self.parameter(msg,1) != 'Admin':
          text = ''
        await self.schreibeNachricht(msg, '***Systemüberblick***  \n' +
        '# <Notiz> - Merker für eigenen Notizen, vom System ignoriert\n' + 
        'Bewegen <Modul> \n'+
        'AnzeigeStatus \n'+
        'Anzeige <Modul>\n'+
        'Energie <Modul> <Wert>\n'+
        '<Modul>Energie <Wert>\n'+
        '<Modul>Anzeige \n'+
        '<Modul>Verhaeltnis <Wert>\n' +
        'Postenliste\n' +
        'Posten <Posten> +/-\n' +
        'Postenreset\n' +
        'Modul\n'+
        'Modulliste\n' +
        'ModulSchalten <Modul> [!]\n' +
        'Konsole <Name> <Text> - Text auf Konsole ausgeben\n' +
        'KonsoleLog <Name> [Anzahl] \n' +
        'Lokalisierung\n'+
        text
        )

    async def Shutdown(self,msg):
       await self.SchreibeWerte(msg, 'Erwachen')
       await self.client.logout()

    async def Postenliste(self, msg):
       text = '***Posten***'
       for w in list(self.Werte):
         if w.startswith('Rolle_'):
           name = w[6:]
           text += f'\n{name} - {self.Werte[w]}'
       await self.schreibeNachricht(msg, text)

    async def Modulliste(self, msg):
       text = '***Module***'
       for w in list(self.Werte):
         if w.startswith('Modul_'):
           name = w[6:]
           text += f'\n{name}'
           if self.Werte[w] == 1:
             text += ' *(active)*'
       await self.schreibeNachricht(msg, text)

    async def Hinweisliste(self, msg):
         text = '***Hinweise***'
         for w in list(self.Werte):
           if w.startswith('Hinweis_'):
             name = w[8:]
             text += f'\n{name}'
         await self.schreibeNachricht(msg, text)
    
    async def Ton(self, msg, channel=None, ton=None):
        dest = discord.utils.find(lambda m: m.name==channel and m.category.name==self.Werte['Kategorie_Orte'], msg.guild.voice_channels)
        if dest is not None: 
           # Ton nur abspielen wenn jemand anwesend ist 
           if len(dest.members) > 0: 
             voice = await dest.connect()
             voice.play(discord.FFmpegPCMAudio(ton))
       
    async def Systemnachricht(self, msg):
      # Nachricht an alle Textkonsolen
      text = self.parameter(msg, 1)
      try:
        # prüfen ob es eine vorgefertigte Systemnachricht ist 
        text = self.Werte['Systemnachricht_'+text]
      except:
        pass
      for channel in msg.guild.text_channels:
        if channel.category.name == self.Werte['Kategorie_Konsole']:
          await channel.send(f'***Important System Information***\n{text}')

    async def Systemnachrichten(self, msg):
      text = '***Systemnachrichtentexte***'
      for w in list(self.Werte):
        if w.startswith('Systemnachricht_'):
          name = w[len('Systemnachricht_'):]
          text += f'\n{name}: {self.Werte[w]}'
      await self.schreibeNachricht(msg, text)

    async def Berechtigungen(self, msg):
      text = '***Berechtigungen***\nLegende: Befehl:Modul:Rolle\n*\* - jedes Modul/jede Rolle erlaubt*\n*# - nur im gleichen Modul wie Befehl*\n\n'
      for w in list(self.Werte):
        if w.startswith('Berechtigung_'):
          name = w[len('Berechtigung_'):]
          b = self.Werte[w].replace('*','\*')
          text += f'\n{name}: {b}'
      await self.schreibeNachricht(msg, text)

    async def Berechtigung(self, msg, befehl=None, modul=None, rolle=None):
        # prüft Berechtigung für bestimmte Modul in Abhängigkeit vom Modul und der Rolle 
        # Berechtigung prüfen
        if self.parameter(msg, 0) == 'Berechtigung':
          befehl = self.parameter(msg, 1)
          modul = self.parameter(msg, 2) 
          rolle = self.parameter(msg, 3)
          befehlmodul = modul
        else:
          try:
            modul = self.getOrtChannel(msg).name
          except:
            modul = 'Fehler'
          befehl = self.parameter(msg, 0)
          befehlmodul = self.parameter(msg, 1)
          if befehlmodul == 'Fehler':
            befehlmodul = modul
        rollen = list()
        if rolle is None:
          for w in list(self.Werte):
            if w.startswith('Rolle_') and self.Werte[w] == msg.author.nick:
              rollen.append(w[6:])
        else:
          rollen.append(rolle)
        print(f'Zugriff: {befehl} {modul} {befehlmodul} {rollen}')
        # Backdoor: System darf immer
        if 'System' in rollen:
          return True
        try:
          check = self.Werte['Berechtigung_'+befehl]
          berechtigungen = check.split(';')
          for check in berechtigungen:
            liste = check.split(':')
            if liste[0] == '#':
              liste[0] = befehlmodul
            rint (f'{liste[0]} {liste[1]} {modul}')
            if liste[0] == '*' or modul == liste[0]:
              if liste[1] == '*' or liste[1] in rollen:
                if self.parameter(msg, 0) == 'Berechtigung':
                  await self.schreibeNachricht(msg, 'Access approved.')    
                print ('ok')        
                return True
          # keine Berechtigung gefunden    
          await self.fehler(msg, 'Access denied.')
          return False
        except:
          await self.fehler(msg, 'Syntax error - Access denied.')
          return False 

        # Mögliche Berechtigungen:
        # Befehl:Modul:Rolle
