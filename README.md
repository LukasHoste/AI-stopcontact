# SlimmeStopcontactenVIVES

## testen van optimizers

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
2. Dan naar integrations gaan en Mosquitto broker opzetten.
3. MQTT explorer kijken als het werkt.

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

### Node Red naar influxDB

1. klik op menu -> import en importeer het flows.json bestand.
2. pas in de mqtt payload node de topic aan. (bv. ai-stopcontact/plugs/lamp_plug/SENSOR)
3. pas in de influxDB node aan naar welke measurement de data geschreven wordt (bv. lamp_home)
4. Indien je een andere mqtt broker gebruikt moet je in de mqtt node het server veld aanpassen.

## Sluimerverbruik apparaten

1. Monitor : als de monitor uit is, is het sluimerverbruik = 0W. Waarschijnlijk door de powersave die op de monitor zit.

![monitor_sluimerverbruik](./img/monitor_sluimerverbruik.png)

2. Printer: als het in standby uiteindelijk komt is het 5W. (<5.5)

![printer_sluimerverbruik](./img/printer_sluimerverbruik.png)

3. Computer (van school): als de computer uit is dan heeft het een sluimerverbruik van ong. 1W

![computer_sluimerverbruik](./img/computer_sluimerverbruik.png)

4. Soundboxen: als de boxen uitstaan dan heeft het een sluimerverbruik van 2W -> ingebruik 4-5W

![soundboxen_sluimerverbruik](./img/soudboxen_sluimerverbruik.png)

## Scripts

### Classificatie script

Het classificatie script haalt aan de hand van mqtt samples van een mqtt broker. Van zodra dat er genoeg samples ontvangen zijn kan het een predictie maken. Deze predictie wordt vervolgens teruggestuurd naar een subtopic van de topic waarvan de data komt.

#### Installatie classificatie

```txt
pip install numpy
pip install paho-mqtt
pip install tensorflow
pip install keras
pip install scikit-learn
```

### State predictie script

Dit script...........

#### Installatie state predictie

```txt
pip install numpy
pip install paho-mqtt
pip install tensorflow
pip install keras
pip install joblib
pip install scikit-learn
```

### Always off script

Aan de hand van dit script kan in een dataset gekeken worden op welke uren het apparaat gewoonlijk altijd uitstaat. Het resultaat hiervan wordt opgestuurd naar mqtt om door nodeRED gebruikt te kunnen worden.

## Notebooks

### Classfication

Deze notebook wordt gebruikt om een classificatie model te trainen. Dit model wordt gebruikt in het classificatie script om apparaten te herkennen.

### Prediction state

Deze notebook wordt gebruikt om een LSTM model te trainen. Aan de hand van dit model kan een state van een apparaat voorspeld worden (aan of uit). Momenteel wordt gewerkt met transfer learning wat het model ertoe in staat stelt om 2 à 3 verschillende patronen te herkennen.

## Opstelling

### Touchscreen

Om het touchscreen te gebruiken moet het ten eerste verbonden met het te bedienen apparaat.
Volg voor de initiele instelling de volgende [guide](https://joy-it.net/files/files/Produkte/RB-LCD10-2/RB-LCD-10-2%20Manual-A6%2026-02-20.pdf).
Vervolgens moeten aan de instellingen uit de guide enkele aanpassingen gemaakt worden. De gecalibreerde coördinaten in /usr/share/X11/xorg.conf.d/99-calibration.conf moeten verwijderd worden en de swapaxes option moet ook verwijderd worden. Vervolgens moet de volgende lijn toegevoegd worden aan /usr/share/X11/xorg.conf.d/99-calibration.conf Option "TransformationMatrix" "0 -1 1 1 0 0 0 0 1". Ten laatste moet er nog voor gezorgd worden dat ubuntu xorg en niet wayland gebruikt. Hiervoor moet automatisch inloggen eerst uitgeschakeld worden. Op ubuntu is dit te vinden onder instellingen -> users. Log vervolgens uit en klik bij het inloggen op het tandwiel en selecteer xorg.
