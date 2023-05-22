# Ontwikkelen van een AI-stopcontact

De doelstelling van deze bachelorproef was om op een innovatieve manier het sluimerverbruik van verschillende toestellen te verminderen. Hiervoor werd er gebruik gemaakt van artificiële intelligentie.

Hiervoor werd ten eerste onderzoek uitgevoerd naar het sluimerverbruik van apparaten. Om een stopcontact automatisch aan en uit te zetten moet het sluimerverbruik namelijk duidelijk onderscheidbaar zijn van het normaal verbruik.

## Sluimerverbruik apparaten

1. Monitor : als de monitor uit is, is het sluimerverbruik = 0W. Waarschijnlijk door de powersave die op de monitor zit.

![monitor_sluimerverbruik](./img/monitor_sluimerverbruik.png)

2. Printer: als het in standby uiteindelijk komt is het 5W. (<5.5)

![printer_sluimerverbruik](./img/printer_sluimerverbruik.png)

3. Computer (van school): als de computer uit is dan heeft het een sluimerverbruik van ong. 1W

![computer_sluimerverbruik](./img/computer_sluimerverbruik.png)

4. Soundboxen: als de boxen uitstaan dan heeft het een sluimerverbruik van 2W -> ingebruik 4-5W

![soundboxen_sluimerverbruik](./img/soudboxen_sluimerverbruik.png)

De artificiële intelligentie zal eerst en vooral gaan herkennen welk toestel er zich momenteel bevindt in het stopcontact. Om het toestel te herkennen wordt gebruik gemaakt van een simpel classificatiemodel. Dit model herkent apparaten aan de hand van het effectief vermogen, reactief vermogen, actief vermogen en de stroom. Van deze parameters worden een bepaald aantal samples genomen die als input van het model dienen. Dit model kan slechts een gelimiteerd aantal apparaten herkennen. Hoe meer apparaten het model moet kunnen herkennen hoe slechter de predictie wordt. Om dit probleem op te lossen kan het aantal samples data dat genomen wordt vergroot worden of kan gebruik worden van een LSTM sequence classificatie model. Daarna wordt het gebruikersgedrag opgenomen, hiermee kan de AI een aagneleerd patroon herkennen. Vervolgens zal de AI aan de hand van het herkende patroon een voorspelling maken van de volgende status van het stopcontact. Aan de hand hiervan wordt kan het stopcontact automatisch aan en uitgezet worden. Voor deze AI werd gebruik gemaakt van een LSTM/Long Short Term Memory model.

![LSTM](./img/LSTM.png)
Een LSTM model neemt als input een historiek. Deze historiek kan bestaan uit één of meerdere parameters. Voor ons model werd gebruik gemaakt van de dag van de week, het uur, de minuut en de status op dat moment. Om uit deze historiek te leren wordt in een LSTM model gebruik gemaakt van drie gates. Ten eerste bepaald de input gate welke informatie uit de gekregen historiek belangrijk is voor de voorspelling. Ten tweede bepaald de forget gate welke informatie van vorige voorspellingen nog belangrijk is en dus wel of niet uit het geheugen mag verwijderd worden. Ten laatste bepaalt de output gate welke informatie welke informatie van de huidige voorspelling opgeslagen moet worden.

Om ervoor te zorgen dat het LSTM model voor meerdere apparaten een patroon kan herkennen en voorspellen werd een apparaat parameter toegevoegd. De waarde van deze parameter wordt bepaald aan de hand van het classificatie model en staat het model ertoe in staat om verschillende apparaten van elkaar te onderscheiden. Het ontwikkelde model is er toe in staat om voor een printer, opladende gsm, laptop, pc en speaker een voorspelling te maken. Het model werd voor elk van deze apparaten één patroon aangeleerd. Om ervoor te zorgen dat de voorspellingen van het model voldoende vlug veranderingen vertonen werden de hoeken van het patroon waarmee geleerd wordt afgerond. Om het model uit te breiden kunnen meer apparaten toegevoegd worden en moet een methode gevonden worden om voor elk apparaat meerdere patronen aan te leren.

Ten slotte werd er een opstelling gemaakt waarop alles te zien is en ook volledig bediend kan worden met een touchscreen.
Voor de artificiële intelligentie werden er twee modellen ontworpen. Het eerste model wordt gebruikt om het toestel dat zich in het stopcontact bevindt te herkennen. Om het model te leren is er data nodig. Hiervoor werd het verbruik van verschillende toestellen opgemeten. Het tweede model zal het gebruikerspatroon herkennen om de plug aan of uit te zetten. Om het patroon te leren, werd er data opgemeten van een gebruiker en werd synthetische data aangemaakt.

## Installation guide

[installation guide](./installatie_uitvoering.md)

## Classificatie geteste optimizers

- sgd = niet goed, loss verandert niet goed
- adagrad = niet goed, loss verandert vrijwel niet
- RMSprop = werkt redelijk, maar ook niet echt goed, de loss bereikt nooit een uitstekende waarde
- adam = werkt goed, bereikt vaker een goede waarde dan andere optimizers
- adamax = werkt redelijk, beetje beter dan RMSprop, loss wordt wel niet super goed
- FTRL = werkt goed, loss verlaagt traag, maar verlaagt wel telkens, mss goed met heel veel epochs
- nadam = werkt redelijk, gelijkaardig aan RMSprop

## Home assistant setup

### MQTT broker

1. Install Mosquitto broker in de Add-on store.
2. Ga naar integrations en klik bij de MQTT integration op configure, klik op re-configure en voer de instellingen van je broker in.
3. Indien de broker op home assistant loopt kan MQTT explorer gebruikt worden om te testen of de broker werkt.

### Oplossing Node-red bad gateway

1. Credential secret toevoegen (addons->node-red->configuration)
2. SSL uitzetten (zelfde plek)
3. Opnieuw opstarten van Node-Red

### Shelly plugs

1. Shelly in-pluggen
2. Ga in de shelly app naar add devices en voeg de geselecteerde apparaten toe
3. In de shelly app kan je dan de ip van de plug vinden.

### Tasmota op shelly

1. [Hier](https://templates.blakadder.com/shelly_plug_S.html) is de url voor de install te vinden (https://github.com/arendst/mgos-to-tasmota)
2. Zoek in de lijst je device dat je wil flashen, kopieer de update URL en pas shellyip aan naar de ip van je shelly
3. surf naar deze link, nu zou je plug moeten beginnen flashen -> volg de instructies van tasmota
4. Ga in tasmota naar configuration -> configure template en plak de [configuration](https://templates.blakadder.com/shelly_plug_S.html) hier te vinden in het template veld en zet activate aan -> klik op save. Of ga naar configure Module en selecteer BlitzWolf SHP in de lijst, klik vervolgens op save.
5. Ga in tasmota naar configuration -> configure MQTT, zet als host je mqtt broker (mqtt.devbit.be), zet als topic {naam plug}_plug en zet als full topic ai-stopcontact/plugs/%topic%/
6. Ga in tasmota naar logging en zet 'Telemetry Period' op 10 (seconden).

### Node Red naar influxDB

1. klik op menu -> import en importeer het flows.json bestand.
2. pas in de mqtt payload node de topic aan. (bv. ai-stopcontact/plugs/lamp_plug/SENSOR)
3. pas in de influxDB node aan naar welke measurement de data geschreven wordt (bv. lamp_home)
4. Indien je een andere mqtt broker gebruikt moet je in de mqtt node het server veld aanpassen.

## Scripts

### Classificatie script

Het classificatie script haalt aan de hand van mqtt samples van een broker. Van zodra dat er genoeg samples ontvangen zijn kan het een predictie maken. Deze predictie wordt vervolgens teruggestuurd naar een subtopic van de topic waarvan de data komt. Deze predictie kan éénmaal of meerdere malen uitgevoerd worden.

![classificatie](./img/schema_classificatie.png)

### State predictie script

Dit script kan aan de hand van een historiek voor een apparaat een voorspelling maken van de state van dat apparaat.

![classificatie](./img/schema_voorspelling.png)

### Combinatie script

Dit script combineerd de classificatie en voorspelling met elkaar. In dit script wordt het herkende apparaat gebruikt voor de voorspelling van de state.

### Always off script

Aan de hand van dit script kan in een dataset gekeken worden op welke uren het apparaat gewoonlijk altijd uitstaat. Het is mogelijk om de bekomen uren naar mqtt te sturen zodat ze vervolgens door een andere applicatie gebruikt kunnen worden.

## Notebooks

### Classfication

Dit notebook wordt gebruikt om een classificatie model te trainen. Dit model wordt gebruikt in het classificatie script om apparaten te herkennen.

### Prediction state

Dit notebook wordt gebruikt om een LSTM model te trainen. Aan de hand van dit model kan een state van een apparaat voorspeld worden (aan of uit). In onze simulatie wordt getraind op twee patronen, één voor een box en één voor een laptop.

## Opstelling

hier foto opstelling

## Dashboards

### Classificatie dashboard

![classificatie dashboard](./img/classificatie_dashboard.png)

Het classificatie dashboard wordt gebruikt om te tonen welk apparaat het classificatie script herkend en welk apparaat zou moeten herkend worden.

### Voorspelling dashboard

![voorspelling dashboard](./img/prediction_dashboard.png)

Op het voorspelling dashboard wordt getoond welke waarde momenteel voorspeld wordt, welk apparaat herkend werd en of het stopcontact momenteel aan of uit staat.

### Historiek dashboard

![historiek dashboard](./img/history_dashboard.png)

Het historiek dashboard is een grafana dashboard dat gebruikt wordt om de historiek van de twee apparaten uit de simulatie te tonen.

### Manuele controle dashboard

![manuele controle dashboard](./img/manual_dahboard.png)

Het manuele controle dashboard is een dashboard dat gebruikt wordt om de stopcontacten manueel aan te sturen en dus het automatisch aan- en uitgaan uit te schakelen.

### Touchscreen

Om het touchscreen te gebruiken moet het ten eerste verbonden met het te bedienen apparaat.
Volg voor de initiele instelling de volgende [guide](https://joy-it.net/files/files/Produkte/RB-LCD10-2/RB-LCD-10-2%20Manual-A6%2026-02-20.pdf).
Vervolgens moeten aan de instellingen uit de guide enkele aanpassingen gemaakt worden. De gecalibreerde coördinaten in /usr/share/X11/xorg.conf.d/99-calibration.conf moeten verwijderd worden en de swapaxes option moet ook verwijderd worden. Vervolgens moet de volgende lijn toegevoegd worden aan /usr/share/X11/xorg.conf.d/99-calibration.conf Option "TransformationMatrix" "0 -1 1 1 0 0 0 0 1". Ten laatste moet er nog voor gezorgd worden dat ubuntu xorg en niet wayland gebruikt. Hiervoor moet automatisch inloggen eerst uitgeschakeld worden. Op ubuntu is dit te vinden onder instellingen -> users. Log vervolgens uit en klik bij het inloggen op het tandwiel en selecteer xorg.
