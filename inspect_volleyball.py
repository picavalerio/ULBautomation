import os
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"
ULB_PATH = (
    "/student/bookings/"
    "46e3df5e-ce7e-4c96-b26b-2b34211001a7"
)


def login(page, username, password):
    page.goto(BASE_URL + "/login", wait_until="domcontentloaded")
    page.locator("#email").fill(username)
    page.locator("#password").fill(password)
    page.get_by_role("button", name="Sign In", exact=True).click()

    for _ in range(30):
        if "/student/bookings" in page.url:
            break
        page.wait_for_timeout(1000)

    if "/student/bookings" not in page.url:
        raise RuntimeError("Login non completato: " + page.url)


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        raise RuntimeError("Credenziali mancanti nei GitHub Secrets.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        try:
            login(page, username, password)
            print("LOGIN OK")

            ulb = page.locator(f'a[href="{ULB_PATH}"]')

            if ulb.count() != 1:
                raise RuntimeError(
                    f"Link ULB attesi 1, trovati {ulb.count()}"
                )

            ulb.click()
            page.wait_for_timeout(2500)

            if ULB_PATH not in page.url:
                raise RuntimeError("Pagina ULB non raggiunta.")

            selector = 'button:has(img[alt="Volleyball"])'
            count = page.locator(selector).count()

            print("PULSANTI VOLLEYBALL:", count)

            if count != 3:
                raise RuntimeError(
                    f"Attesi 3 pulsanti, trovati {count}. "
                    "Interrompo senza prenotare."
                )

            for index in range(count):
                button = page.locator(selector).nth(index)

                print(
                    f"\n========== VARIANTE {index + 1}/{count} =========="
                )

                button.click()
                page.wait_for_timeout(1800)

                print("\n--- TESTO PAGINA ---")
                print(page.locator("body").inner_text()[-9000:])

                actions = page.locator("button:visible").filter(
                    has_text="Book"
                )

                print("\n--- CARD CON AZIONE BOOK ---")
                print("BOTTONI TROVATI:", actions.count())

                for card_index in range(actions.count()):
                    action = actions.nth(card_index)

                    details = action.evaluate("""
                        el => {
                            const result = [];
                            let node = el;

                            for (
                                let level = 0;
                                level < 6 && node;
                                level++
                            ) {
                                result.push({
                                    level,
                                    tag: node.tagName,
                                    className: String(
                                        node.className || ""
                                    ).slice(0, 250),
                                    text: (
                                        node.innerText || ""
                                    ).trim().slice(0, 1200),
                                    html: node.outerHTML.slice(0, 3500)
                                });

                                node = node.parentElement;
                            }

                            return result;
                        }
                    """)

                    print(f"\nCARD {card_index + 1}")

                    for item in details:
                        print(
                            f"\nLEVEL {item['level']} "
                            f"{item['tag']}"
                        )
                        print("CLASS:", item["className"])
                        print("TESTO:", item["text"])
                        print("HTML:", item["html"])

            print(
                "\nISPEZIONE COMPLETATA. "
                "NESSUNA PRENOTAZIONE EFFETTUATA."
            )

        finally:
            browser.close()


if __name__ == "__main__":
    main()
