import os
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_URL = "https://nova-sport-v1-web.vercel.app"


def inspect_page(page):
    print("\n=== PAGINA DOPO IL LOGIN ===")
    print("URL:", page.url)
    print("Titolo:", page.title())

    print("\n=== INTESTAZIONI ===")
    for heading in page.locator("h1, h2, h3").all_inner_texts():
        print(repr(heading.strip()))

    print("\n=== PULSANTI VISIBILI ===")
    buttons = page.locator("button:visible").all_inner_texts()
    for button in buttons:
        print(repr(button.strip()))

    print("\n=== LINK VISIBILI ===")
    links = page.locator("a:visible").evaluate_all("""
        elements => elements.map(el => ({
            text: (el.innerText || '').trim(),
            path: (() => {
                try {
                    const u = new URL(el.href);
                    return u.pathname;
                } catch {
                    return '';
                }
            })()
        }))
    """)
    for link in links:
        print(link)

    print("\n=== SEZIONI CON RUOLO ===")
    elements = page.locator(
        '[role="tab"], [role="navigation"], [role="alert"]'
    ).evaluate_all("""
        elements => elements.map(el => ({
            role: el.getAttribute('role'),
            text: (el.innerText || '').trim().slice(0, 200)
        }))
    """)
    for element in elements:
        print(element)

    print("\n=== CAMPI ANCORA VISIBILI ===")
    fields = page.locator("input:visible").evaluate_all("""
        elements => elements.map(el => ({
            type: el.type,
            id: el.id,
            placeholder: el.placeholder
        }))
    """)
    for field in fields:
        print(field)


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

        try:
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")

            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            print("Campi login compilati.")
            print("Invio del modulo di accesso...")

            page.get_by_role(
                "button",
                name="Sign In",
                exact=True
            ).click()

            try:
                page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=10000
                )
            except PlaywrightTimeoutError:
                pass

            page.wait_for_timeout(4000)

            if page.locator("#password:visible").count() > 0:
                print("\nLOGIN NON CONFERMATO.")
                print("La pagina mostra ancora il campo password.")

                alerts = page.locator(
                    '[role="alert"], [aria-live="polite"], [aria-live="assertive"]'
                ).all_inner_texts()

                for alert in alerts:
                    print("Messaggio:", alert.strip())

                inspect_page(page)
                sys.exit(2)

            print("\nLOGIN APPARENTEMENTE RIUSCITO.")
            inspect_page(page)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
