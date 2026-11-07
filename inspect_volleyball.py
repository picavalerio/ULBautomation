import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"
ULB_PATH = "/student/bookings/46e3df5e-ce7e-4c96-b26b-2b34211001a7"


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        raise RuntimeError("Credenziali mancanti.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        try:
            # Login
            page.goto(BASE_URL + "/login",
                      wait_until="domcontentloaded")
            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            page.get_by_role(
                "button", name="Sign In", exact=True
            ).click()

            page.wait_for_url(
                "**/student/bookings",
                timeout=20000
            )
            page.wait_for_timeout(1500)

            print("LOGIN RIUSCITO")

            # Apriamo ULB cliccando il link, non con goto().
            ulb_link = page.locator(f'a[href="{ULB_PATH}"]')

            print("Link ULB trovati:", ulb_link.count())

            if ulb_link.count() != 1:
                raise RuntimeError("Link ULB non identificato.")

            ulb_link.click()
            page.wait_for_timeout(3000)

            print("\nURL:", page.url)

            print("\n=== TESTO PAGINA ===")
            print(page.locator("body").inner_text()[:5000])

            print("\n=== TUTTI I PULSANTI VISIBILI ===")
            visible_buttons = page.locator("button:visible")

            for i in range(visible_buttons.count()):
                b = visible_buttons.nth(i)
                print(
                    i,
                    "TEXT:", repr(b.inner_text()),
                    "ARIA:", repr(b.get_attribute("aria-label")),
                    "HTML:", b.evaluate("(el) => el.outerHTML[:500]")
                )

            print("\n=== CONFRONTO SELETTORI VOLLEYBALL ===")
            print(
                "get_by_role exact:",
                page.get_by_role(
                    "button", name="Volleyball", exact=True
                ).count()
            )
            print(
                "locator button text:",
                page.locator("button").filter(
                    has_text="Volleyball"
                ).count()
            )
            print(
                "get_by_text exact:",
                page.get_by_text(
                    "Volleyball", exact=True
                ).count()
            )

        finally:
            browser.close()


if __name__ == "__main__":
    main()
