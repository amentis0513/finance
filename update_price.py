import time
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def run_with_page_timeout(url, stock, page_timeout=8, wait_for_table=10, driver=None):

    try:
        # 设置页面加载超时时间（秒）
        driver.set_page_load_timeout(page_timeout)
        try:
            print(
                f"Calling driver.get with page load timeout = {page_timeout}s...",
                flush=True,
            )
            driver.get(url)
            print("driver.get completed normally.", flush=True)
        except TimeoutException as e:
            # 当超时发生，我们捕获它并继续——浏览器仍然存在并可能部分加载页面
            print(
                f"driver.get timed out after {page_timeout}s, continuing. Exception: {e}",
                flush=True,
            )

        print("Current URL:", driver.current_url, flush=True)
        print("Title:", driver.title, flush=True)

        # 现在尝试等待我们真正关心的元素（例如表格行）一段较长时间（可单独指定）
        wait = WebDriverWait(driver, wait_for_table)
        try:
            row_css = "table tbody tr"
            print(
                f"Waiting up to {wait_for_table}s for table rows to appear...",
                flush=True,
            )
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, row_css)))
            rows = driver.find_elements(By.CSS_SELECTOR, row_css)
            print(f"Found {len(rows)} rows (limited to first 20):", flush=True)
            prices = []
            for i, row in enumerate(rows[:21], start=2):
                cols = row.find_elements(By.TAG_NAME, "td")
                # print(i, len(cols), [c.text for c in cols[:6]])
                prices.append(float(cols[4].text))
                print(i, float(cols[4].text))
            if prices:
                # write the prices to a file named ./stocks/{stock}_prices.txt
                with open(f"./stocks/{stock}_prices.txt", "w") as f:
                    for price in prices:
                        f.write(str(price) + "\n")
        except Exception as e:
            print(
                "Did not find table rows within wait time or other error:",
                repr(e),
                flush=True,
            )
            # 诊断：打印 page_source 长度与前面片段
            src = driver.page_source or ""
            print("page_source length:", len(src), flush=True)
            print("page_source (first 1000 chars):")
            print(src[:1000], flush=True)

    finally:
        print("Quitting driver...", flush=True)
        try:
            return
        except Exception:
            pass


if __name__ == "__main__":
    # open hsi_list.txt and get the list of stock codes
    # with open("hsi_list.txt", "r") as f:
    #     stock_codes = [line.strip() for line in f.readlines() if line.strip()]
    opts = Options()
    # 视情况选择 headless 或不，为调试建议显示界面
    # opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    stock_codes = ["0005.HK", "0001.HK"]  # Example stock codes for testing
    try:
        driver = webdriver.Chrome(options=opts)
    except WebDriverException as e:
        print("Failed to start Chrome webdriver:", e, file=sys.stderr, flush=True)
        sys.exit(1)
    for stock in stock_codes:
        url = f"https://hk.finance.yahoo.com/quote/{stock}/history/"
        run_with_page_timeout(
            url, stock=stock, page_timeout=8, wait_for_table=10, driver=driver
        )

    driver.quit()
