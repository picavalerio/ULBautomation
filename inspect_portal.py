import os
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"
ULB_PATH = "/student/bookings/46e3df5e-ce7e-4c96-b26b-2b34211001a7"


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        print("Credenziali mancanti.")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        try:
            # Login
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")
            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            page.get_by_role(
                "button", name="Sign In", exact=True
            ).click()

            page.wait_for_url("**/student/bookings", timeout=20000)
            page.wait_for_timeout(1500)

            print("LOGIN RIUSCITO")

            # Individuazione e apertura del collegamento ULB
            ulb_link = page.locator(f'a[href="{ULB_PATH}"]')

            if ulb_link.count() != 1:
                print("ERRORE: collegamento ULB non identificato univocamente.")
                sys.exit(2)

            print("Collegamento ULB identificato.")
            ulb_link.click()

            page.wait_for_timeout(3000)

            print("\n=== PAGINA ULB ===")
            print("URL:", page.url)
            print("Titolo:", page.title())

            print("\n=== TESTO VISIBILE ===")
            print(page.locator("body").inner_text()[:6000])

            print("\n=== INTESTAZIONI ===")
            for heading in page.locator("h1, h2, h3, h4").all_inner_texts():
                print(repr(heading.strip()))

            print("\n=== PULSANTI VISIBILI ===")
            for button in page.locator("button:visible").all_inner_texts():
                print(repr(button.strip()))

            print("\n=== LINK VISIBILI ===")
            links = page.locator("a:visible").evaluate_all("""
                elements => elements.map(el => ({
                    text: (el.innerText || '').trim(),
                    path: (() => {
                        try {
                            return new URL(el.href).pathname;
                        } catch {
                            return '';
                        }
                    })()
                }))
            """)

            for link in links:
                print(link)

            print("\n=== ELEMENTI CON TESTO VOLLEYBALL ===")
            volleyball = page.get_by_text("Volleyball", exact=True)

            for i in range(volleyball.count()):
                item = volleyball.nth(i)
                print(item.evaluate("""
                    el => ({
                        tag: el.tagName,
                        className: String(el.className || ''),
                        parentTag: el.parentElement?.tagName || '',
                        parentClass: String(
                            el.parentElement?.className || ''
                        ).slice(0, 200)
                    })
                """))

        finally:
            browser.close()


if __name__ == "__main__":
    main()
