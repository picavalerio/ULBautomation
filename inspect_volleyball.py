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
            auth_status = []

            def log_response(response):
                url = response.url.lower()

                if (
                    "auth/v1/token" in url
                    or "/auth/redirect" in url
                ):
                    auth_status.append(response.status)
                    print(
                        "AUTH:",
                        response.status,
                        response.url.split("?")[0]
                    )

            page.on("response", log_response)

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

            for _ in range(30):
                if "/student/bookings" in page.url:
                    break
                page.wait_for_timeout(1000)

            if "/student/bookings" not in page.url:
                print("LOGIN NON COMPLETATO")
                print("URL:", page.url)
                print(
                    page.locator("body").inner_text()[:2000]
                )
                raise RuntimeError("Login non riuscito.")

            print("\nLOGIN RIUSCITO.")

            # 2. APERTURA ULB
            page.wait_for_timeout(1500)

            ulb_link = page.locator(
                f'a[href="{ULB_PATH}"]'
            )

            print("Link ULB trovati:", ulb_link.count())

            if ulb_link.count() != 1:
                raise RuntimeError(
                    "Non è stato identificato un solo link ULB."
                )

            ulb_link.click()
            page.wait_for_timeout(3000)

            print("\n=== PAGINA ULB ===")
            print("URL:", page.url)

            if ULB_PATH not in page.url:
                raise RuntimeError(
                    "La navigazione alla pagina ULB non è riuscita."
                )

            # 3. TESTO DELLA PAGINA
            print("\n=== TESTO PAGINA ULB ===")
            print(
                page.locator("body").inner_text()[:7000]
            )

            # 4. ISPEZIONE DEGLI ELEMENTI VOLLEYBALL
            print("\n=== ELEMENTI VOLLEYBALL ===")

            volleyball = page.get_by_text(
                "Volleyball",
                exact=True
            )

            count = volleyball.count()
            print("Occorrenze trovate:", count)

            for i in range(count):
                item = volleyball.nth(i)

                print(
                    f"\n========== ELEMENTO {i + 1} =========="
                )

                details = item.evaluate("""
                    el => {
                        const result = [];
                        let current = el;

                        for (let j = 0; j < 7 && current; j++) {
                            result.push({
                                tag: current.tagName,
                                id: current.id || "",
                                className: String(
                                    current.className || ""
                                ).slice(0, 300),
                                text: (
                                    current.innerText || ""
                                ).trim().slice(0, 600),
                                html: current.outerHTML.slice(
                                    0, 1800
                                )
                            });

                            current = current.parentElement;
                        }

                        return result;
                    }
                """)

                for level, element in enumerate(details):
                    print(f"\n--- LIVELLO {level} ---")
                    print("TAG:", element["tag"])
                    print("ID:", element["id"])
                    print("CLASS:", element["className"])
                    print("TESTO:", element["text"])
                    print("HTML:", element["html"])

            # 5. PULSANTI VISIBILI
            print("\n=== PULSANTI VISIBILI ===")

            buttons = page.locator("button:visible")
            print("Totale:", buttons.count())

            for i in range(buttons.count()):
                button = buttons.nth(i)

                print(
                    f"\nPULSANTE {i + 1}",
                    "TESTO:", repr(button.inner_text()),
                    "ARIA:", repr(
                        button.get_attribute("aria-label")
                    ),
                    "TYPE:", repr(
                        button.get_attribute("type")
                    )
                )

            # 6. PROGRAMMA E SLOT
            print("\n=== PROGRAMME SOLBOSCH ===")

            programme = page.get_by_text(
                "Programme Solbosch",
                exact=True
            )

            print(
                "Occorrenze esatte:",
                programme.count()
            )

            for i in range(programme.count()):
                print(
                    f"\nPROGRAMMA {i + 1}:",
                    programme.nth(i).evaluate(
                        "(el) => el.parentElement.outerHTML.slice(0, 2000)"
                    )
                )

            print("\n=== FONDO PAGINA ===")
            print(
                page.locator("body").inner_text()[-5000:]
            )

            print("\nISPEZIONE TERMINATA.")
            print("NESSUNA PRENOTAZIONE EFFETTUATA.")

        finally:
            browser.close()


if __name__ == "__main__":
    main()
