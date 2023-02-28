# SlimmeStopcontactenVIVES

[code - notebook](https://colab.research.google.com/drive/1pjBKEyINliCrKm2UD8AyNFnTkva3qZNF?usp=sharing)

## model tests

### 2 hidden layers 8 -> 5 met rmsprop, batch_size = 8 en telkens relu 50 epochs

loss 0.3232 en vall_los 0.3177

### 2 hidden layers 8 -> 5 met adam, batch_size = 16 en telkens relu 50 epochs

### 2 hidden layers 25 -> 25 met adam, batch_size = 32 en telkens relu 50 epochs

loss 0.2414 en vall_los 0.2392

### 2 hidden layers 100 -> 50 met rmsprop, batch_size = 16 en telkens relu 50 epochs

### 2 hidden layers 5 -> 3 met adam, batch_size = 16 en telkens relu 50 epochs

loss 0.2084 vall_los 0.2125

### 2 hidden layers 50 -> 15 met rmsprop, batch_size = 16 en telkens relu 50 epochs

## testen van optimizers

- sgd = niet goed, loss verandert niet goed
- adagrad = niet goed, loss verandert vrijwel niet
- RMSprop = werkt redelijk, maar ook niet echt goed, de loss bereikt nooit een uitstekende waarde
- adam = werkt goed, bereikt vaker een goede waarde dan andere optimizers
- adamax = werkt redelijk, beetje beter dan RMSprop, loss wordt wel niet super goed
- FTRL = werkt goed, loss verlaagt traag, maar verlaagt wel telkens, mss goed met heel veel epochs
- nadam = werkt redelijk, gelijkaardig aan RMSprop

## Home assistant setup voorlopig

### MQTT broker

1. Install Mosquitto broker in de Add-on store.
2. Dan naar integrations gaan en Mosquitto broker opzetten.
3. MQTT explorer kijken als het werkt.

### Fix Node-red bad gateway

1. Credential secret toevoegen (addons->node-red->configuration)
2. SSL uitzetten (zelfde plek)
3. Opnieuw opstarten van Node-Red

### Shelly

1. Shelly in-pluggen en verbinden met zijn hotspot: 192.168.33.1
2. Dan onder internet & security de wifi mode instellen op iotlab
3. Dan via de shelly app kan je zijn nieuwe IP terugvinden (zorg ervoor dat de cloud nog niet is uitgezet)
4. Dan onder internet & security de cloud uitzetten en ten laatste onder de advanced developer settings, enable je de MQTT met de username hetzelfde als dat van de homeassitant + passw en de IP van de homeassistant.

## Tasmota op shelly

1. [Hier](https://templates.blakadder.com/shelly_plug_S.html) is de url voor de install te vinden (https://github.com/arendst/mgos-to-tasmota)
2. Zoek in de lijst je device dat je wil flashen, kopieer de update URL en pas shellyip aan naar de ip van je shelly
3. surf naar deze link, nu zou je plug moeten beginnen flashen -> volg de instructies van tasmota
4. Ga in tasmota naar configuration -> configure Module en selecteer BlitzWolf SHP in de lijst, klik vervolgens op save.

## Sluimerverbruik apparaten

1. Monitor : als de monitor uit is, is het sluimerverbruik = 0W. Waarschijnlijk door de powersave die op de monitor zit.

![monitor_sluimerverbruik](./img/monitor_sluimerverbruik.png)

2. Printer: als het in standby uiteindelijk komt is het 5W. (<5.5)

![printer_sluimerverbruik](./img/printer_sluimerverbruik.png)

3. Computer (van school): als de computer uit is dan heeft het een sluimerverbruik van ong. 1W

![computer_sluimerverbruik](./img/computer_sluimerverbruik.png)

4. Soundboxen: als de boxen uitstaan dan heeft het een sluimerverbruik van 2W -> ingebruik 4-5W

![soundboxen_sluimerverbruik](./img/soudboxen_sluimerverbruik.png)
