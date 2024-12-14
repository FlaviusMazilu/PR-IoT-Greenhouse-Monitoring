# Proiect - Sera de flori

## Introducere
### Descriere proiect
Proiectul presupune un sistem de monitorizare a calitatii ambientale intr-un solar de flori/plante in care sunt monitorizati factori precum intensitatea luminoasa si temperatura aerului. Ca si actuatori avem niste switch-uri care vor porni sistemul de incalzire sau vor aprinde lumini, in functie de comenzile primite.

## Arhitectura
### Diagrama componente
![alt text](image-1.png)



### Protocoale folosite:
- Pentru comunicarea senzorilor si a actuatorilor va fi folosit protocolul `MQTT`, iar un `server local`(in cazul nostru un laptop va fi mai mult decat suficient) va avea pe de o parte rol de `MQTT broker`.
- Totodata, un `alt proces` de pe serverul central va fi la randul lui un `SUBSCRIBER` pentru informatiile primite de la senzori, pe care le va pasa mai departe la instanta locala de `vizualizare a datelor`(Grafana/Chart.js).
- Pentru a putea avea conectivitate de pe orice device din afara retelei locale, voi folosi Ngrok pe post de front-door, care creaza un tunel criptat intre serverul local si serverul lor, oferind un endpoint pe care il pot accesa de oriunde.
