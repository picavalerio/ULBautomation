import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"

ULB_PATH = (
    "/student/bookings/"
    "46e3df5e-ce7e-4c96-b26b-2b34211001a7"
)


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
            # 1. LOGIN
            page.goto(
                BASE_URL + "/login",
                wait_until="domcontentloaded"
            )

            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            print("Invio login...")

            page.get_by_role(
                "button",
                name="Sign In",
                exact=True
            ).click()

            # Attesa del redirect.
            for _ in range(30):
                if "/student/bookings" in page.url:
                    break
                page.wait_for_timeout(1000)

            if "/student/bookings" not in page.url:
                print("LOGIN NON COMPLETATO")
                print("URL:", page.url)
                print(
                    page.locator("body").inner_text()[:1500]
                )
                raise RuntimeError("Login fallito.")

            print("LOGIN RIUSCITO")

            # 2. APERTURA ULB
            page.wait_for_timeout(1500)

            ulb_link = page.locator(
                f'a[href="{ULB_PATH}"]'
            )

            if ulb_link.count() != 1:
                raise RuntimeError(
                    "Collegamento ULB non identificato."
                )

            ulb_link.click()
            page.wait_for_timeout(3000)

            print("\n=== PAGINA ULB ===")
            print("URL:", page.url)

            # 3. TESTO PAGINA
            print("\n=== TESTO PAGINA ===")
            print(
                page.locator("body").inner_text()[:7000]
            )

            # 4. ELEMENTI VOLLEYBALL
            print("\n=== ELEMENTI VOLLEYBALL ===")

            volleyball = page.get_by_text(
                "Volleyball",
                exact=True
            )

            print(
                "Occorrenze:",
                volleyball.count()
            )

            for i in range(volleyball.count()):
                item = volleyball.nth(i)

                print(
                    f"\n========== VOLLEYBALL {i + 1} =========="
                )

                details = item.evaluate("""
                    el => {
                        const result = [];
                        let current = el;

                        for (let j = 0; j < 6 && current; j++) {
                            result.push({
                                tag: current.tagName,
                                id: current.id,
                                className: String(
                                    current.className || ''
                                ).slice(0, 250),
                                text: (
                                    current.innerText || ''
                                ).trim().slice(0, 700),
                                html: current.outerHTML.slice(
                                    0, 1500
                                )
                            });

                            current = current.parentElement;
                        }

                        return result;
                    }
                """)

                for level, element in enumerate(details):
                    print(f"\nLIVELLO GENITORE {level}")
                    print("TAG:", element["tag"])
                    print("ID:", element["id"])
                    print("CLASS:", element["className"])
                    print("TESTO:", element["text"])
                    print("HTML:", element["html"])

            # 5. PULSANTI VISIBILI
            print("\n=== PULSANTI VISIBILI ===")

            buttons = page.locator("button:visible")

            print("Numero:", buttons.count())

            for i in range(buttons.count()):
                button = buttons.nth(i)

                print(
                    i + 1,
                    repr(button.inner_text()),
                    "ARIA:",
                    repr(button.get_attribute("aria-label"))
                )

            # 6. SLOT VISIBILI
            print("\n=== POSSIBILI SLOT ===")

            print(
                page.locator("body").inner_text()[-5000:]
            )

            print("\nISPEZIONE COMPLETATA.")
            print("NESSUNA PRENOTAZIONE EFFETTUATA.")

        finally:
            browser.close()


if __name__ == "__main__":
    main()
