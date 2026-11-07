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
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")
            page.locator("#email").fill(username)
            page.locator("#password").fill(password)
            page.get_by_role(
                "button", name="Sign In", exact=True
            ).click()

            page.wait_for_url("**/student/bookings", timeout=20000)
            page.goto(BASE_URL + ULB_PATH, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            buttons = page.get_by_role("button", name="Volleyball", exact=True)

            print("NUMERO PULSANTI VOLLEYBALL:", buttons.count())

            for i in range(buttons.count()):
                button = buttons.nth(i)

                print(f"\n========== VOLLEYBALL {i + 1} ==========")

                print("HTML PULSANTE:")
                print(button.evaluate("(el) => el.outerHTML"))

                print("\nSTRUTTURA GENITORI:")
                print(button.evaluate("""
                    el => {
                        const result = [];
                        let current = el;

                        for (let i = 0; i < 5 && current; i++) {
                            result.push({
                                tag: current.tagName,
                                id: current.id,
                                className: String(current.className || '').slice(0, 250),
                                text: (current.innerText || '').trim().slice(0, 700),
                                html: current.outerHTML.slice(0, 1200)
                            });
                            current = current.parentElement;
                        }

                        return result;
                    }
                """))

        finally:
            browser.close()


if __name__ == "__main__":
    main()
