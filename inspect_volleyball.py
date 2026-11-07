import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    print("Username presente:", bool(username))
    print("Password presente:", bool(password))
    print("Lunghezza username:", len(username or ""))
    print("Lunghezza password:", len(password or ""))

    if not username or not password:
        raise RuntimeError("Credenziali mancanti.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(BASE_URL + "/login",
                      wait_until="domcontentloaded")

            email_field = page.locator("#email")
            password_field = page.locator("#password")

            email_field.fill(username)
            password_field.fill(password)

            print("Tipo campo email:",
                  email_field.get_attribute("type"))
            print("Valore email inserito:",
                  repr(email_field.input_value()))
            print("Email valida secondo il browser:",
                  email_field.evaluate(
                      "(el) => el.checkValidity()"
                  ))

            page.get_by_role(
                "button", name="Sign In", exact=True
            ).click()

            page.wait_for_timeout(5000)

            print("\nURL finale:", page.url)
            print("Testo pagina:")
            print(page.locator("body").inner_text()[:2000])

        finally:
            browser.close()


if __name__ == "__main__":
    main()
