"""Starter sicuro: per ora valida la configurazione e verifica i Secrets.
La navigazione e i selettori Nova Sport verranno aggiunti dopo i passaggi descritti dall'utente.
"""
import os
import sys
from pathlib import Path
import yaml

def load_config():
    with Path("config.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        print("ERRORE: configura NOVA_USERNAME e NOVA_PASSWORD nei GitHub Secrets.")
        sys.exit(2)

    booking = cfg.get("booking", {})
    print("Configurazione caricata.")
    print(f"Università: {cfg.get('university')}")
    print(f"Corso: {cfg.get('course')}")
    print(f"Giorno/orario: {booking.get('weekday')} {booking.get('start_time')}-{booking.get('end_time')}")
    print(f"Livello: {booking.get('level') or '(non specificato)'}")
    print(f"Dry run: {booking.get('dry_run', True)}")
    print("Credenziali presenti: sì (valori mai stampati).")

    if not booking.get("enabled", False):
        print("PRENOTAZIONE DISATTIVATA: imposta enabled: true solo dopo i test.")
        return

    if not booking.get("dry_run", True):
        print("ATTENZIONE: modalità prenotazione richiesta, ma l'automazione del portale non è ancora implementata.")
        sys.exit(3)

    print("Modalità dry-run: nessuna pagina aperta e nessuna prenotazione eseguita.")

if __name__ == "__main__":
    main()
