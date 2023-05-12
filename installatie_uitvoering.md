# Installatie en uitvoering

Hieronder is er terug te vinden wat er moet geïnstalleerd worden en hoe de notebooks en scripts moeten uitgevoerd worden.

## Installatie

### Github

Alle uit te voeren code is te vinden op github. Github is een platform dat programmeurs toestaat om te bewaren en te beheren. Daarnaast laat het toe om aanpassingen aan de code te bewaren en te controleren. Om code van github te halen moet er eerst de ssh key van je apparaat op github toegevoegd worden. Indien je nog geen ssh key hebt, kan deze gegeneerd worden aan de hand van de onderstaande commando.

```txt
ssh-keygen 
```

Vervolgens kan je aan de hand van het volgende commando je ssh key kopiëren.

```txt
cat [locatie bestand]/.ssh/id_rsa.pub
```

Op windows bevind het bestand zich in de user directory en op linux in de home directory. Vervolgens moet deze key toegevoegd worden op github onder settings “SSH and GPG keys”, selecteer hier new “ssh key” en plak je key. Nu de key toegevoegd is moet nog git geïnstalleerd worden voor de code opgehaald kan worden. Op windows kan git geïnstalleerd worden via de [volgende link](https://git-scm.com/download/win) en op Linux kan het geïnstalleerd worden met het volgende commando.

```txt
sudo apt install git
```

Om code van github te “clonen” kan nu op een repository op de code knop gedrukt worden waarna op ssh geklikt worden en de gegenereerde string kan gekopieerd worden. Aan de hand van het onderstaand commando kan de code opgehaald worden.

```txt
git clone [gekopieerde string]
```

## Uitvoering

### Trainen modellen

Onder notebooks kunnen de jupyter notebooks gevonden worden die gebruikt werden voor het trainen van de twee AI-modellen.

### Trainen van classificatie model

Voor het herkennen van apparaten wordt het … notebook gebruikt. Om dit notebook uit te voeren moet ten eerste python geïnstalleerd worden. Python is makkelijk te installeren via de download pagina op de officiële python website. Voor het trainen van de modellen werd telkens gebruik gemaakt van python 3.9.7. Vervolgens moeten modules geïnstalleerd worden die te vinden zijn in de onderstaande tabel.

```txt
sudo apt install python3-pip
python -m pip install -U matplotlib
pip3 install numpy
pip3 install joblib
pip3 install pandas
pip3 install tensorflow
pip3 install -U scikit-learn
```

Om het model te trainen kan gebruik gemaakt worden van eigen data of van onze data. Om gebruik te maken van eigen data moet de bestandslocatie in de volgende twee lijnen code aangepast worden.

```python
for file in os.listdir("../data/28-03+afstands"):

df = pd.read_csv("../data/28-03+afstands/" + objectClass + ".csv")
```

Daarnaast moet het voldoen aan de structuur zoals besproken in ‘Benodigde data’. Indien je over meer of minder data beschikt is het een goed idee om de SAMPLES_PER_CLASS parameter respectief te verhogen of te verlagen. Ook kan het nodig zijn dat het aantal neuronen, de batch size, de dropout en het aantal epochs voor optimale prestatie van het model moeten aangepast worden.

### Trainen van gebruikersgedrag model

Voor het voorspellen van een gebruikersgedrag wordt het … notebook gebruikt. Om dit model te runnen, moeten de onderstaande modules geïnstalleerd zijn.

```txt
sudo apt install python3-pip
python -m pip install -U matplotlib
pip3 install numpy
pip3 install joblib
pip3 install pandas
pip3 install tensorflow
pip3 install -U scikit-learn
```

Om eigen data te gebruiken moeten de onderstaande lijnen code aangepast worden, waarbij de ‘own_file’ zal moeten vervangen worden naar de naam van de eigen dataset.

```python
df_pc = load_data(r'../data/multiple_devices/new_weeks/[own_file].csv')
df_box = load_data(r'../data/multiple_devices/new_weeks/[own_file].csv')
```

Indien de historiek kleiner is dan een week of verspringt met een grotere of kleinere time step moet de waarde van de ‘time_steps’ variabele aangepast worden. Om het model optimaal te laten werken kunnen de lagen, het maken van de slope, de learning rate en de batch size aangepast worden.

## Uitvoeren van scripts

Voor het uitvoeren van de scripts moeten ten eerste de onderstaande modules geïnstalleerd worden. Deze modules kunnen geïnstalleerd worden aan de hand van pip of pip3.

```txt
pip3 install numpy
pip3 install joblib
pip3 install pandas
pip3 install tensorflow
pip3 install scikit-learn
pip3 install paho-mqtt
pip3 install influxdb
pip3 install python-dotenv
```

Vervolgens kunnen de scripts simpel uitgevoerd worden aan de hand van het commando [1]. Om het combinatie script uit te voeren met argumenten moet het commando gewijzigd worden aan de hand van het help commando [2].

```txt
python3 [naam bestand]
python3 [naam bestand] –help
```

In de verschillende scripts kunnen de modellen aangepast worden door in de lijnen [1] en [2] het pad naar het model aan te passen. Belangrijk bij het gebruiken van een ander model is dat hierbij ook de scaler moet aangepast worden. Dit kan aangepast worden in de lijnen [3] en [4]. In de scripts die een voorspelling maken kan de historiek die gebruikt wordt voor de simulatie aangepast worden in de lijnen [5].

```python
model = keras.models.load_model('/[own_path]/[model_folder]')
classification_model = keras.models.load_model('/[own_path]/[model_folder')

scaler = joblib.load('/[own_path]/[scaler_name].gz')
classification_scaler = joblib.load('/[own_path]/[scaler_name].gz')

df_history = pd.read_csv(r'/[own_path]/[own_history].csv', parse_dates=['timestamp'])
```
