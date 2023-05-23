# Home assistant & tasmota setup

## MQTT broker

1. Install Mosquitto broker in de Add-on store.
2. Ga naar integrations en klik bij de MQTT integration op configure, klik op re-configure en voer de instellingen van je broker in.
3. Indien de broker op home assistant loopt kan MQTT explorer gebruikt worden om te testen of de broker werkt.

## Oplossing Node-red bad gateway

1. Credential secret toevoegen (addons->node-red->configuration)
2. SSL uitzetten (zelfde plek)
3. Opnieuw opstarten van Node-Red

## Shelly plugs

1. Shelly in-pluggen
2. Ga in de shelly app naar add devices en voeg de geselecteerde apparaten toe
3. In de shelly app kan je dan de ip van de plug vinden.

## Tasmota op shelly

1. [Hier](https://templates.blakadder.com/shelly_plug_S.html) is de url voor de install te vinden (https://github.com/arendst/mgos-to-tasmota)
2. Zoek in de lijst je device dat je wil flashen, kopieer de update URL en pas shellyip aan naar de ip van je shelly
3. surf naar deze link, nu zou je plug moeten beginnen flashen -> volg de instructies van tasmota
4. Ga in tasmota naar configuration -> configure template en plak de [configuration](https://templates.blakadder.com/shelly_plug_S.html) hier te vinden in het template veld en zet activate aan -> klik op save. Of ga naar configure Module en selecteer BlitzWolf SHP in de lijst, klik vervolgens op save.
5. Ga in tasmota naar configuration -> configure MQTT, zet als host je mqtt broker (mqtt.devbit.be), zet als topic {naam plug}_plug en zet als full topic ai-stopcontact/plugs/%topic%/
6. Ga in tasmota naar logging en zet 'Telemetry Period' op 10 (seconden).

## Node Red naar influxDB

1. Klik op menu -> import en importeer het flows.json bestand.
2. Pas in de mqtt payload node de topic aan. (bv. ai-stopcontact/plugs/lamp_plug/SENSOR)
3. Pas in de influxDB node aan naar welke measurement de data geschreven wordt (bv. lamp_home)
4. Indien je een andere mqtt broker gebruikt moet je in de mqtt node het server veld aanpassen.
