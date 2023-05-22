# Korte uitleg over notebooks & scripts

## Notebooks

### Classfication

Dit notebook wordt gebruikt om een classificatie model te trainen. Dit model wordt gebruikt in het classificatie script om apparaten te herkennen.

### Prediction state

Dit notebook wordt gebruikt om een LSTM model te trainen. Aan de hand van dit model kan een state van een apparaat voorspeld worden (aan of uit). In onze simulatie wordt getraind op twee patronen, één voor een box en één voor een laptop.

## Scripts

### Classificatie script

Het classificatie script haalt aan de hand van mqtt samples van een broker. Van zodra dat er genoeg samples ontvangen zijn kan het een predictie maken. Deze predictie wordt vervolgens teruggestuurd naar een subtopic van de topic waarvan de data komt. Deze predictie kan éénmaal of meerdere malen uitgevoerd worden.

![classificatie](../img/schema_classificatie.png)

### State predictie script

Dit script kan aan de hand van een historiek voor een apparaat een voorspelling maken van de state van dat apparaat.

![classificatie](../img/schema_voorspelling.png)

### Combinatie script

Dit script combineerd de classificatie en voorspelling met elkaar. In dit script wordt het herkende apparaat gebruikt voor de voorspelling van de state.

### Always off script

Aan de hand van dit script kan in een dataset gekeken worden op welke uren het apparaat gewoonlijk altijd uitstaat. Het is mogelijk om de bekomen uren naar mqtt te sturen zodat ze vervolgens door een andere applicatie gebruikt kunnen worden.
