# NobulaRepo
Nobula, general developer test

Kako bi pokrenuli rješenje potrebno je imati instaliranu posljednju verziju Python-a. 

Klonirati repozitorij negdje na računar, te navigirati preko terminala do njega. Zatim pokrenuti sljedeće komande:

``` 
$ pip install -r requirements.txt
$ python app.py
```

Napravljen je Swagger za UI. Nakon pokretanja aplikacije, pokrenuti http://localhost:5000/apidocs/#/default za prikaz.

Ima više vrsta rješenja za korake. Ovdje ću ih ukratko objasniti:

Prva i drugi korak je rješen na dva načina: 
1. Dobijanje prostih brojeva sa Eratostenovim sitom. Čuvanje rješenja (niza prostih brojeva) u cache memoriji, te na taj način optimizuje sljedeći poziv ako je pozvan sa istim argumentom.
2. Dobijanje prostih brojeva sa O(sqrt(N)) metodom. Ova metoda ima isto čuvanje cache memorije kao prvo rješenje, ali ima i dodatnu mogućnost da uzima najbliže/najbolje rješenje te nastavlja od njeg. Na taj način pozivi za brojeve koji su veći od onih koje smo predhodno pozvali su brži.

Treći korak je rješen također na više načina:
1. Moguće je obrisati poseban podatak koji je predhodno pozvan (postoje dva requsta vezana za ovo koja ovise o tome kako je pozvnam prvi korak)
2. Moguće je obrisati određeni broj podataka u cache memoriji
3. Moguće je obrisati sve iz cache memorije

Takođe postoji sistem brisanja cache memorije u određeno vrijeme. Moguće je namjestiti vrijeme brisanja preko timeout/time metode.

Četvrti korak
Postoji endpoint kojim se može obrisati sva cache memorija
Postoji GET metoda koja pokazuje koji se sve elementi nalaze u bazi/cache memoriji.

