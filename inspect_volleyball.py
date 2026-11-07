import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        raise RuntimeError("Credenziali mancanti nei GitHub Secrets.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        # Registriamo le risposte del server relative al login.
        page.on("response", lambda response: print(
            "HTTP", response.status, response.url
        ) if "/auth/" in response.url else None)

        try:
            page.goto(BASE_URL + "/login",
                      wait_until="domcontentloaded")

            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            print("Invio del modulo di login...")

            page.get_by_role(
                "button", name="Sign In", exact=True
            ).click()

            # Lasciamo tempo al portale di completare il login.
            page.wait_for_timeout(6000)

            print("\n=== RISULTATO LOGIN ===")
            print("URL:", page.url)
            print("Titolo:", page.title())
            print("\n=== TESTO VISIBILE ===")
            print(page.locator("body").inner_text()[:3000])

            if "/student/bookings" not in page.url:
                print("\nLOGIN NON COMPLETATO.")
                return

            print("\nLOGIN RIUSCITO.")

        finally:
            browser.close()


if __name__ == "__main__":
    main()
