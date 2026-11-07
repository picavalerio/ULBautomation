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
