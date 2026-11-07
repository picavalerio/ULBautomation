import os
import sys
from playwright.sync_api import sync_playwright


BASE_URL = "https://nova-sport-v1-web.vercel.app"

ULB_HREF = (
    "/student/bookings/"
    "46e3df5e-ce7e-4c96-b26b-2b34211001a7"
)


def login(page, username, password):
    print("\n========== LOGIN ==========")

    auth_responses = []

    def log_auth_response(response):
        if "/auth/v1/token" in response.url:
            auth_responses.append({
                "status": response.status,
                "url": response.url.split("?")[0]
            })
            print(
                "Risposta autenticazione HTTP:",
                response.status
            )

        elif "/auth/redirect" in response.url:
            print(
                "Risposta redirect HTTP:",
                response.status
            )

    page.on("response", log_auth_response)

    page.goto(
        BASE_URL + "/login",
        wait_until="domcontentloaded"
    )

    page.locator("#email").wait_for(
        state="visible",
        timeout=15000
    )

    page.locator("#email").fill(username)
    page.locator("#password").fill(password)

    print("Invio del modulo...")

    page.get_by_role(
        "button",
        name="Sign In",
        exact=True
    ).click()

    try:
        page.wait_for_url(
            "**/student/bookings**",
            timeout=30000
        )

    except Exception:
        print("\nLOGIN NON CONFERMATO")
        print("URL finale:", page.url)
        print("Risposte autenticazione:", auth_responses)

        try:
            print("\nTesto visibile della pagina:")
            print(page.locator("body").inner_text()[:2500])
        except Exception:
            print("Impossibile leggere il testo della pagina.")

        raise RuntimeError(
            "Login non completato o redirect non riuscito."
        )

    print("Login riuscito.")
    print("URL:", page.url)


def open_ulb(page):
    print("\n========== APERTURA ULB ==========")

    ulb_link = page.locator(
        f'a[href="{ULB_HREF}"]'
    )

    ulb_link.wait_for(
        state="visible",
        timeout=15000
    )

    ulb_link.click()

    page.wait_for_load_state(
        "domcontentloaded",
        timeout=20000
    )

    print("Pagina ULB aperta:", page.url)

    page.get_by_text(
        "Book a Timeslot",
        exact=True
    ).wait_for(
        state="visible",
        timeout=15000
    )


def print_programme(page):
    print("\n--- PROGRAMMA VISUALIZZATO ---")

    badges = page.locator("span").evaluate_all(
        """elements => elements
            .filter(el => el.textContent.trim() !== "")
            .filter(el =>
                el.textContent.trim() === "Programme Solbosch" ||
                el.textContent.trim() === "Personnel Programme Solbosch" ||
                el.textContent.trim() === "Erasme"
            )
            .map(el => ({
                text: el.textContent.trim(),
                html: el.outerHTML
            }))
        """
    )

    if badges:
        for badge in badges:
            print("Programma:", badge["text"])
            print("HTML:", badge["html"])
    else:
        print("Nessun badge programma trovato.")

    print("\nTesto della pagina (primi 10000 caratteri):")
    print(page.locator("body").inner_text()[:10000])


def inspect_booking_buttons(page):
    print("\n--- PULSANTI DELLE LEZIONI ---")

    buttons = page.locator("button").evaluate_all(
        """elements => elements
            .map((el, index) => ({
                index: index,
                text: el.innerText.trim(),
                visible: !!(el.offsetWidth || el.offsetHeight),
                className: el.className
            }))
            .filter(el =>
                ["Book", "FULL", "JOIN WAITING LIST"].includes(el.text)
                && el.visible
            )
        """
    )

    if not buttons:
        print("Nessun pulsante Book/FULL/Waiting List trovato.")
        return

    for button in buttons:
        print(
            f"\nPulsante #{button['index']}: "
            f"{button['text']}"
        )
        print("Classi:", button["className"])

        # Ispeziona gli antenati del pulsante per identificare
        # la card che contiene corso, data, orario e disponibilità.
        html = page.locator("button").nth(
            button["index"]
        ).evaluate(
            """el => {
                let current = el;
                const result = [];

                for (let i = 0; i < 5 && current; i++) {
                    result.push({
                        level: i,
                        tag: current.tagName,
                        className: current.className,
                        text: (current.innerText || "").trim().slice(0, 1500),
                        html: current.outerHTML.slice(0, 5000)
                    });

                    current = current.parentElement;
                }

                return result;
            }"""
        )

        for ancestor in html:
            print(
                f"\n ANTENATO livello {ancestor['level']}: "
                f"{ancestor['tag']}"
            )
            print(" Classi:", ancestor["className"])
            print(" Testo:", ancestor["text"])
            print(" HTML:", ancestor["html"])


def inspect_volleyball(page):
    print("\n========== ISPEZIONE VOLLEYBALL ==========")

    volleyball_buttons = page.locator("button").filter(
        has=page.locator('img[alt="Volleyball"]')
    )

    count = volleyball_buttons.count()

    print("Pulsanti Volleyball trovati:", count)

    if count == 0:
        raise RuntimeError(
            "Nessun pulsante Volleyball trovato."
        )

    for index in range(count):
        print("\n")
        print("=" * 70)
        print(f"VOLLEYBALL PULSANTE {index + 1} DI {count}")
        print("=" * 70)

        # Seleziona esclusivamente il pulsante dello sport.
        volleyball_buttons.nth(index).click()

        # Attende il caricamento dei contenuti dinamici.
        page.wait_for_timeout(1200)

        selected_button = volleyball_buttons.nth(index)

        print("\nHTML del pulsante selezionato:")
        print(
            selected_button.evaluate(
                "el => el.outerHTML.slice(0, 1000)"
            )
        )

        print_programme(page)

        inspect_booking_buttons(page)

    print("\n========== ISPEZIONE TERMINATA ==========")
    print("Nessuna prenotazione effettuata.")


def main():
    username = os.getenv("NOVA_USERNAME")
    password = os.getenv("NOVA_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Credenziali mancanti nei GitHub Secrets "
            "NOVA_USERNAME e NOVA_PASSWORD."
        )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        try:
            page.set_default_timeout(15000)

            login(page, username, password)

            open_ulb(page)

            inspect_volleyball(page)

        finally:
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERRORE:", str(error))
        sys.exit(1)
