import os
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_URL = "https://nova-sport-v1-web.vercel.app"


def safe_path(url):
    parsed = urlparse(url)
    return parsed.path


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        print("Credenziali mancanti nei GitHub Secrets.")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        # Diagnostica: registriamo solo URL senza query string,
        # codici HTTP e messaggi tecnici. Mai payload o credenziali.
        page.on("response", lambda response: print(
            f"HTTP {response.status} {safe_path(response.url)}"
            if any(word in response.url.lower()
                   for word in ["auth", "login", "session", "sign"])
            else None
        ))

        page.on("requestfailed", lambda request: print(
            "RICHIESTA FALLITA:",
            safe_path(request.url),
            request.failure
        ))

        page.on("pageerror", lambda error: print(
            "ERRORE JAVASCRIPT:", str(error)[:500]
        ))

        page.on("console", lambda message: print(
            "CONSOLE ERROR:", message.text[:500]
            if message.type == "error" else ""
        ) if message.type == "error" else None)

        try:
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")

            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            print("Invio del modulo...")
            page.get_by_role(
                "button", name="Sign In", exact=True
            ).click()

            page.wait_for_timeout(7000)

            print("\n=== RISULTATO ===")
            print("URL:", page.url)
            print("Titolo:", page.title())

            print("\n=== TESTO VISIBILE DELLA PAGINA ===")
            print(page.locator("body").inner_text()[:4000])

            print("\n=== CAMPI VISIBILI ===")
            fields = page.locator("input:visible").evaluate_all("""
                elements => elements.map(el => ({
                    type: el.type,
                    id: el.id,
                    placeholder: el.placeholder
                }))
            """)
            for field in fields:
                print(field)

            print("\n=== PULSANTI ===")
            for button in page.locator("button:visible").all_inner_texts():
                print(repr(button.strip()))

        finally:
            browser.close()


if __name__ == "__main__":
    main()
