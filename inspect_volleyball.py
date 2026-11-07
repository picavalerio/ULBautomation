import os
import sys
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
        raise RuntimeError(
            "Credenziali mancanti nei GitHub Secrets."
        )

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        try:

            # =====================================
            # 1. LOGIN
            # =====================================

            page.goto(
                BASE_URL + "/login",
                wait_until="domcontentloaded"
            )

            page.locator("#email").fill(username)
            page.locator("#password").fill(password)

            print("Invio del modulo di login...")

            page.get_by_role(
                "button",
                name="Sign In",
                exact=True
            ).click()

            # Attesa del redirect fino a 30 secondi.
            # Non dipende da un singolo evento di navigazione.

            for attempt in range(30):

                if "/student/bookings" in page.url:
                    break

                page.wait_for_timeout(1000)

            if "/student/bookings" not in page.url:

                print("\nLOGIN NON COMPLETATO")
                print("URL:", page.url)

                print(
                    "TESTO:",
                    page.locator("body").inner_text()[:1500]
                )

                raise RuntimeError(
                    "Impossibile completare il login."
                )

            print("\nLOGIN RIUSCITO")

            page.wait_for_timeout(1500)

            # =====================================
            # 2. APERTURA ULB
            # =====================================

            ulb_link = page.locator(
                f'a[href="{ULB_PATH}"]'
            )

            print(
                "Link ULB trovati:",
                ulb_link.count()
            )

            if ulb_link.count() != 1:

                raise RuntimeError(
                    "Collegamento ULB non identificato "
                    "univocamente."
                )

            ulb_link.click()

            page.wait_for_timeout(3000)

            print("\n=== PAGINA ULB ===")
            print("URL:", page.url)
            print("Titolo:", page.title())

            # =====================================
            # 3. TESTO DELLA PAGINA
            # =====================================

            print("\n=== TESTO PAGINA ===")

            print(
                page.locator("body").inner_text()[:7000]
            )

            # =====================================
            # 4. PULSANTI VISIBILI
            # =====================================

            print("\n=== TUTTI I PULSANTI VISIBILI ===")

            visible_buttons = page.locator(
                "button:visible"
            )

            print(
                "Numero pulsanti:",
                visible_buttons.count()
            )

            for i in range(visible_buttons.count()):

                button = visible_buttons.nth(i)

                print(f"\nPULSANTE {i + 1}")

                print(
                    "TEXT:",
                    repr(button.inner_text())
                )

                print(
                    "ARIA:",
                    repr(button.get_attribute("aria-label"))
                )

                print(
                    "HTML:",
                    button.evaluate(
                        "(el) => el.outerHTML.slice(0, 500)"
                    )
                )

            # =====================================
            # 5. CONFRONTO SELETTORI VOLLEYBALL
            # =====================================

            print(
                "\n=== CONFRONTO SELETTORI VOLLEYBALL ==="
            )

            role_count = page.get_by_role(
                "button",
                name="Volleyball",
                exact=True
            ).count()

            button_text_count = page.locator(
                "button"
            ).filter(
                has_text="Volleyball"
            ).count()

            text_count = page.get_by_text(
                "Volleyball",
                exact=True
            ).count()

            print(
                "get_by_role exact:",
                role_count
            )

            print(
                "locator button text:",
                button_text_count
            )

            print(
                "get_by_text exact:",
                text_count
            )

            # =====================================
            # 6. DETTAGLIO DEI TRE VOLLEYBALL
            # =====================================

            print(
                "\n=== ELEMENTI VOLLEYBALL ==="
            )

            volleyball = page.get_by_text(
                "Volleyball",
                exact=True
            )

            print(
                "Occorrenze Volleyball:",
                volleyball.count()
            )

            for i in range(volleyball.count()):

                item = volleyball.nth(i)

                print(
                    f"\n========== VOLLEYBALL {i + 1} =========="
                )

                print(
                    item.evaluate("""
                        el => {
                            const result = [];
                            let current = el;

                            for (
                                let j = 0;
                                j < 5 && current;
                                j++
                            ) {
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
                                        0, 1200
                                    )
                                });

                                current = current.parentElement;
                            }

                            return result;
                        }
                    """)
                )

            print("\nISPEZIONE COMPLETATA.")
            print("Nessuna prenotazione effettuata.")

        finally:

            browser.close()


if __name__ == "__main__":
    main()
