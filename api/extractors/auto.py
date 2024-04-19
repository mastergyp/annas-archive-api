from time import sleep
CF_TITLE = "Just a moment"


def fix_cf_just_moment(url: str, driver, TRY_COUNT=5):
    # Fix CF `Just moment...` loading
    try_number = 0
    bypass = False

    while try_number < TRY_COUNT:
        print( "INFO", f"Attempting to bypass Cloudflare - Attempt {try_number+1}")

        driver.uc_open_with_reconnect(url, 3)

        try:
            driver.switch_to_frame("iframe")
            driver.uc_click("span.mark")
            sleep(5)
        except Exception:
            pass

        if CF_TITLE not in driver.title:
            print("SUCCESS", "Successfully bypassed Cloudflare.")
            bypass = True
            break

        try_number += 1

    if not bypass:
        print( "ERROR", "Unable to bypass Cloudflare after multiple attempts.")
        raise Exception("Failed to bypass Cloudflare.")
