import requests
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from playwright.sync_api import sync_playwright


TELEGRAM_TOKEN = "7741918636:AAEd0JkRfUCP0KS_7A2yGSE5pEDnLsG5A0o"
TELEGRAM_CHAT_ID = "1412412145"

def notify_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def run(playwright):
    browser = playwright.chromium.launch(headless=False)  # set headless=True if you don't want a browser window
    context = browser.new_context(
        viewport={"width": 762, "height": 695}
    )
    page = context.new_page()

    # Step 1: Navigate to the appointment page
    page.goto("https://pieraksts.mfa.gov.lv/en/egypt/index")

    # Fill in the form
    page.fill('#Persons\\[0\\]\\[first_name\\]', 'rida')
    page.fill('#Persons\\[0\\]\\[last_name\\]', 'rd2000')
    page.fill('#e_mail', 'rida@gmail.com')
    page.fill('#e_mail_repeat', 'rida@gmail.com')
    page.fill('#phone', '+212620839109')

    # Click "Next step"
    page.click('#step1-next-btn > button')

    # Wait for navigation to step2
    page.wait_for_url("https://pieraksts.mfa.gov.lv/en/egypt/step2")

    # Step 2: Choose service
    # Click on the category title to expand
    page.click("div.form-services--title")

    # Select the first available service
    page.click("div.services--wrapper > div:nth-of-type(1) > span")

    # Select the first available sub-service
    page.click("section.active span")

    # Click "Add"
    page.click("section.active > div.description-text--wrapper button")

    # Click "Next step" to proceed
    page.click("#step2-next-btn > button")

    # You can continue with step 3, date picking, etc. here...

    # Optional: keep the browser open or close
    # browser.close()
    # ✅ Now check available dates using browser-side fetch (CORS-safe)
    available_response = page.evaluate(
        """async () => {
            const res = await fetch('https://pieraksts.mfa.gov.lv/en/calendar/available-month-dates?year=2025&month=6', {
                method: 'GET',
                credentials: 'same-origin'
            });
            return await res.text();
        }"""
    )

    notify_telegram("📅 Response from available-month-dates:"+available_response)

    last_date = page.evaluate(
        """async () => {
            const res = await fetch('https://pieraksts.mfa.gov.lv/en/calendar/last-available-date', {
                method: 'GET',
                credentials: 'same-origin'
            });
            return await res.text();
        }"""
    )

    notify_telegram("🕓 Last available date:"+last_date)

    # Optional decision-making logic
    if "Currently all dates are fully booked" in available_response:
        notify_telegram("❌ Aucun créneau disponible pour juin 2025.")
    else:
        notify_telegram("✅ Des créneaux peuvent être disponibles. Continuer vers la sélection de date...")

    # TODO: Continuer avec step3 en fonction de la date si souhaité

    # browser.close()  # Si tu veux fermer automatiquement

with sync_playwright() as playwright:
    run(playwright)