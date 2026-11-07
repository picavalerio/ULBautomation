import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        raise RuntimeError("Credenziali mancanti nei Secrets.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Registra soltanto URL e stato HTTP.
            def log_response(response):
                url = response.url.lower()

                if (
                    "auth/v1/token" in url
                    or "/auth/redirect" in url
                ):
                    print(
                        "AUTH RESPONSE:",
                        response.status,
                        response.url.split("?")[0]
                    )

            page.on("response", log_response)

            page.goto(
                BASE_URL + "/login",
                wait_until="domcontentloaded"
            )

            print("Pagina login caricata.")

            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            print("Campi compilati.")
            print("Invio login...")

            page.get_by_role(
                "button",
                name="Sign In",
                exact=True
            ).click()

            # Attende fino a 20 secondi il redirect.
            for _ in range(20):
                if "/student/bookings" in page.url:
                    break
                page.wait_for_timeout(1000)

            print("\n=== RISULTATO ===")
            print("URL:", page.url)

            if "/student/bookings" in page.url:
                print("LOGIN RIUSCITO.")
            else:
                print("LOGIN NON CONFERMATO.")

                print("\n=== MESSAGGI VISIBILI ===")
                print(
                    page.locator("body").inner_text()[:2500]
                )

                print("\n=== CAMPI LOGIN ===")
                print(
                    "Email presente:",
                    page.locator("#email").count() > 0
                )
                print(
                    "Password presente:",
                    page.locator("#password").count() > 0
                )

        finally:
            browser.close()


if __name__ == "__main__":
    main()
