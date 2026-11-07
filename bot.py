import os
import sys
import yaml
from pathlib import Path
from playwright.sync_api import sync_playwright

CONFIG_FILE = Path(__file__).parent / "config.yaml"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def validate_config(config):
    target = config["target"]

    required = [
        "sport",
        "programme_description",
        "weekday",
        "course_name",
        "time_slot"
    ]

    for field in required:
        if not target.get(field):
            raise ValueError(f"Configurazione mancante: {field}")

    if config["safety"]["book_only_first_match"] is not True:
        raise ValueError("book_only_first_match deve essere true")


def main():

    config = load_config()
    validate_config(config)

    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        print("Credenziali mancanti nei GitHub Secrets.")
        sys.exit(1)

    target = config["target"]

    print("Configurazione caricata.")
    print("Sport:", target["sport"])
    print("Programma:", target["programme_description"])
    print("Giorno:", target["weekday"])
    print("Corso:", target["course_name"])
    print("Orario:", target["time_slot"])

    if not config["safety"]["enabled"]:
        print("Bot disattivato.")
        return

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        base_url = config["portal"]["base_url"]
        bookings_path = config["portal"]["bookings_path"]

        page.goto(
            base_url + bookings_path,
            wait_until="domcontentloaded"
        )

        print("Pagina aperta:", page.url)

        # Controllo iniziale: il portale potrebbe
        # reindirizzare alla pagina di login.
        if "login" in page.url.lower():
            print("Login richiesto: automazione interrotta.")
            browser.close()
            sys.exit(2)

        print("Pagina bookings raggiunta.")

        # PROSSIMA FASE:
        # 1. Autenticazione con le credenziali.
        # 2. Selezione ULB.
        # 3. Selezione dello sport.
        # 4. Verifica del programma.
        # 5. Ricerca della lezione.
        # 6. Verifica disponibilità.
        # 7. Prenotazione e verifica conferma.

        print("Navigazione delle lezioni non ancora attivata.")

        browser.close()


if __name__ == "__main__":
    main()
