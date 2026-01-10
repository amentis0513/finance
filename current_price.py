import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

XPATH_PRICE = '//*[@id="main-content-wrapper"]/section[1]/div[2]/div[1]/section/div/section/div[1]/div[1]/span'


def get_current_price(
    url,
    stock,
    driver,
    page_timeout=8,
    wait_for_table=10,
):

    try:
        # 设置页面加载超时时间（秒）
        driver.set_page_load_timeout(page_timeout)

        try:
            print(f"Getting URL: {url} with stock {stock}", flush=True)
            driver.get(url)
            print("driver.get completed normally.", flush=True)
        except TimeoutException as e:
            # 当超时发生，我们捕获它并继续——浏览器仍然存在并可能部分加载页面
            print(
                f"driver.get timed out after {page_timeout}s, continuing. Exception: {e}",
                flush=True,
            )
            return None

        # 现在尝试等待我们真正关心的元素（例如表格行）一段较长时间（可单独指定）
        wait = WebDriverWait(driver, wait_for_table)
        try:
            row_css = "table tbody tr"
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, row_css)))
            rows = driver.find_elements(By.CSS_SELECTOR, row_css)
            cols = rows[1].find_elements(By.TAG_NAME, "td")
            price = cols[4].text
            return float(price.replace(",", ""))
        except Exception as e:
            print(
                "Did not find table rows within wait time or other error:",
                repr(e),
                flush=True,
            )
            # 诊断：打印 page_source 长度与前面片段
            src = driver.page_source or ""
            print(f"Finish extracting prices for {stock}", flush=True)
            return None
    finally:
        pass


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
