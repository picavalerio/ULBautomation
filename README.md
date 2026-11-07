# ULB Volleyball booking bot — starter

Questo è uno scheletro iniziale: **non effettua ancora login né prenotazioni**.
Serve a predisporre configurazione e GitHub Actions in modo sicuro.

## 1. Configurazione del corso

Modifica `config.yaml`. Le credenziali non vanno mai inserite in questo file.

## 2. Crea il repository GitHub

Crea un repository, preferibilmente privato, e carica questi file.

## 3. Aggiungi le credenziali come GitHub Secrets

Repository → Settings → Secrets and variables → Actions → New repository secret.

Crea:
- `NOVA_USERNAME`
- `NOVA_PASSWORD`

Non inserirle nel codice, nei commit, nei log o nei messaggi.

## 4. Primo test

Lascia `booking.enabled: false` e `dry_run: true`.
In Actions puoi avviare manualmente `ULB Volleyball booking` con **Run workflow**.
Il test controlla solo la configurazione e la presenza dei Secrets.

## 5. Fuso orario

Il workflow è pianificato alle 08:01 in `Europe/Brussels`. GitHub supporta il fuso IANA nei workflow programmati, ma l'avvio può comunque subire ritardi dovuti al carico del servizio: non è una garanzia di esecuzione al secondo.

## Prossimo sviluppo

Dopo che mi avrai descritto i passaggi del portale (ULB → Volleyball → giorno → slot), implementeremo i selettori Playwright. Prima faremo test in sola lettura; il click su BOOK resterà disabilitato finché non avremo verificato corrispondenza e conferma.
