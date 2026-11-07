from playwright.sync_api import sync_playwright

BASE_URL = "https://nova-sport-v1-web.vercel.app"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(10000)

        try:
            page.goto(BASE_URL + "/login", wait_until="domcontentloaded")
            page.locator("body").wait_for()

            print("\n=== PAGINA LOGIN ===")
            print("URL:", page.url)
            print("Titolo:", page.title())

            print("\n=== CAMPI INPUT VISIBILI ===")
            fields = page.locator("input:visible").evaluate_all("""
                elements => elements.map((el, i) => ({
                    index: i,
                    type: el.type,
                    name: el.name,
                    id: el.id,
                    placeholder: el.placeholder,
                    autocomplete: el.autocomplete,
                    ariaLabel: el.getAttribute('aria-label')
                }))
            """)
            for field in fields:
                print(field)

            print("\n=== PULSANTI VISIBILI ===")
            buttons = page.locator("button:visible").all_inner_texts()
            for button in buttons:
                print(repr(button))

            print("\n=== FORM ===")
            forms = page.locator("form").evaluate_all("""
                elements => elements.map(form => ({
                    action: form.getAttribute('action'),
                    method: form.getAttribute('method')
                }))
            """)
            for form in forms:
                print(form)

            print("\n=== TITOLI ===")
            headings = page.locator("h1, h2, h3").all_inner_texts()
            for heading in headings:
                print(repr(heading))

        finally:
            browser.close()

if __name__ == "__main__":
    main()
