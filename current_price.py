import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

XPATH_PRICE = '//*[@id="main-content-wrapper"]/section[1]/div[2]/div[1]/section/div/section/div[1]/div[1]/span'


def get_current_price(url, stock, driver):

    try:
        try:
            driver.get(url)
        except TimeoutException:
            # continue even if page load timed out
            pass

        # Now explicitly wait up to this many seconds for the price element to appear
        wait = WebDriverWait(driver, 5)
        try:
            el = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_PRICE)))
            # Print only the price text
            print(f"{stock} with current price: {el.text}")
            # print(el.text)
        except TimeoutException:
            # element didn't appear in time -> print nothing (or print an error)
            # We'll print nothing as you requested only the price; but to help debug uncomment:
            print(f"ERROR: {stock} price element not found", file=sys.stderr)
            pass

    finally:
        return float(el.text)


if __name__ == "__main__":
    # open hsi_list.txt and get the list of stock codes
    with open("hsi_list.txt", "r") as f:
        stock_codes = [line.strip() for line in f.readlines() if line.strip()]
    opts = Options()
    # Use headless (new) for recent Chrome; fallback to older "--headless" if needed
    # opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--log-level=3")

    try:
        driver = webdriver.Chrome(options=opts)
    except WebDriverException as e:
        print("webdriver_error:", e, file=sys.stderr)
        sys.exit(1)

    # set a page load timeout so driver.get won't block forever
    driver.set_page_load_timeout(5)  # seconds

    for stock in stock_codes:
        url = f"https://hk.finance.yahoo.com/quote/{stock}/history/"
        get_current_price(url, stock=stock, driver=driver)

    driver.quit()
