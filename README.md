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
- nadam = werkt redelijk, gelijkaardag aan RMSprop
