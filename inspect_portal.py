import os
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"


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
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")
            page.locator("#email").fill(username)
            page.locator("#password").fill(password)
            page.get_by_role("button", name="Sign In", exact=True).click()

            page.wait_for_url("**/student/bookings", timeout=20000)
            page.wait_for_timeout(2000)

            print("LOGIN RIUSCITO")
            print("URL:", page.url)

            heading = page.get_by_text("Book a Facility", exact=True).first

            if heading.count() == 0:
                print("Sezione Book a Facility non trovata.")
                sys.exit(2)

            print("\n=== STRUTTURA DELLA SEZIONE ===")

            structure = heading.evaluate("""
                el => {
                    const result = [];
                    let current = el;

                    for (let i = 0; i < 5 && current; i++) {
                        result.push({
                            level: i,
                            tag: current.tagName,
                            id: current.id || '',
                            className: String(current.className || '').slice(0, 200),
                            role: current.getAttribute('role') || '',
                            controls: Array.from(
                                current.querySelectorAll(
                                    'button, a, [role="button"]'
                                )
                            ).map(item => ({
                                tag: item.tagName,
                                text: (item.innerText || '').trim().slice(0, 100),
                                ariaLabel: item.getAttribute('aria-label') || '',
                                href: item.getAttribute('href') || '',
                                disabled: item.disabled || false
                            })).slice(0, 30)
                        });

                        current = current.parentElement;
                    }

                    return result;
                }
            """)

            for item in structure:
                print(item)

            print("\n=== ELEMENTI ESATTI CON TESTO ULB ===")

            ulb_elements = page.get_by_text("ULB", exact=True)

            for i in range(ulb_elements.count()):
                item = ulb_elements.nth(i)

                info = item.evaluate("""
                    el => {
                        const parent = el.parentElement;
                        return {
                            tag: el.tagName,
                            className: String(el.className || ''),
                            parentTag: parent ? parent.tagName : '',
                            parentClass: parent
                                ? String(parent.className || '').slice(0, 200)
                                : '',
                            clickableAncestor: (() => {
                                const c = el.closest(
                                    'button, a, [role="button"]'
                                );
                                return c ? {
                                    tag: c.tagName,
                                    text: (c.innerText || '').trim().slice(0, 100),
                                    href: c.getAttribute('href') || ''
                                } : null;
                            })()
                        };
                    }
                """)

                print(info)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
