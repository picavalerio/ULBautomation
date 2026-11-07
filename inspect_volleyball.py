import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        raise RuntimeError("GitHub Secrets mancanti.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", lambda response: print(
            f"HTTP {response.status} {response.url}"
        ) if "/auth/" in response.url else None)

        page.on("requestfailed", lambda request: print(
            "REQUEST FAILED:",
            request.url,
            request.failure
        ) if "/auth/" in request.url else None)

        try:
            page.goto(
                BASE_URL + "/login",
                wait_until="domcontentloaded"
            )

            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            print("Email presente:", bool(
                page.locator("#email").input_value()
            ))
            print("Email valida:", page.locator(
                "#email"
            ).evaluate("(el) => el.checkValidity()"))

            print("Invio login...")

            page.get_by_role(
                "button",
                name="Sign In",
                exact=True
            ).click()

            # Attesa fino a 30 secondi.
            for _ in range(30):
                if "/student/bookings" in page.url:
                    break
                page.wait_for_timeout(1000)

            print("\n=== RISULTATO ===")
            print("URL:", page.url)

            print("\n=== MESSAGGI VISIBILI ===")
            print(page.locator("body").inner_text()[:2000])

            print("\n=== CAMPI LOGIN ===")
            print("Email:", page.locator(
                "#email"
            ).input_value())

            print("Password presente:", bool(
                page.locator("#password").input_value()
            ))

        finally:
            browser.close()


if __name__ == "__main__":
    main()
