import sys
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from current_price import get_current_price
from update_price import run_with_page_timeout

if __name__ == "__main__":
    with open("hsi_list.txt", "r") as f:
        stock_codes = [line.strip() for line in f.readlines() if line.strip()]
    opts = Options()

    # check if ./stocks directory exists, if not create it
    if not os.path.exists("./stocks"):
        os.makedirs("./stocks")

    # 视情况选择 headless 或不，为调试建议显示界面
    # opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    if "update" in sys.argv:

        try:
            driver = webdriver.Chrome(options=opts)
        except WebDriverException as e:
            print("Failed to start Chrome webdriver:", e, file=sys.stderr, flush=True)
            sys.exit(1)
        count = 1
        for stock in stock_codes:
            print(f"{count}: Processing {stock}", flush=True)
            count += 1
            url = f"https://hk.finance.yahoo.com/quote/{stock}/history/"
            run_with_page_timeout(
                url, stock=stock, page_timeout=8, wait_for_table=10, driver=driver
            )

        driver.quit()

    if "cal" in sys.argv:

        # Categorize stocks by z-score
        cat_a = "MUST BUY (跌穿)"
        cat_b = "CAN BUY (between -2 and 0)"
        cat_c = "HOLD (between 0 and 2)"
        cat_d = "0 CAN SELL (above 2)"
        categories = {
            cat_a: [],
            cat_b: [],
            cat_c: [],
            cat_d: [],
        }

        try:
            driver = webdriver.Chrome(options=opts)
        except WebDriverException as e:
            print("Failed to start Chrome webdriver:", e, file=sys.stderr, flush=True)
            sys.exit(1)
        count = 1
        for stock in stock_codes:
            print(f"{count}: Processing {stock}", flush=True)
            count += 1

            # check whether "./stocks/{stock}_prices.txt" exists
            if not os.path.exists(f"./stocks/{stock}_prices.txt"):
                print(
                    f"Price history file for {stock} does not exist, skipping...",
                    flush=True,
                )
                continue

            url = f"https://hk.finance.yahoo.com/quote/{stock}/history/"
            current_price = get_current_price(url, stock=stock, driver=driver)
            if current_price is None:
                print(
                    f"Could not get current price for {stock}, skipping...", flush=True
                )
                continue
            # get all data from ./stocks/{stock}_prices.txt and calculate mean and sd to get the z score of the current price
            # use try, else continue if file not found or empty
            try:
                with open(f"./stocks/{stock}_prices.txt", "r") as f:
                    prices = [
                        float(line.strip()) for line in f.readlines() if line.strip()
                    ]
            except Exception as e:
                print(f"Could not read prices for {stock}: {e}", flush=True)
                continue

            mean = sum(prices) / len(prices)
            variance = sum((p - mean) ** 2 for p in prices) / (len(prices) - 1)
            sd = variance**0.5
            z_score = (current_price - mean) / sd
            print(f"{stock} Z-Score: {z_score:.4f}")

            if z_score < -2:
                categories[cat_a].append((stock, z_score))
            elif -2 <= z_score < 0:
                categories[cat_b].append((stock, z_score))
            elif 0 <= z_score < 2:
                categories[cat_c].append((stock, z_score))
            else:  # z >= 2
                categories[cat_d].append((stock, z_score))

        driver.quit()

        # print summary
        for cat, stocks in categories.items():
            stocks.sort(key=lambda x: x[1])
            print(f"Category: {cat} (Total {len(stocks)})")
            count = 1
            for ticker, z in stocks:
                print(f"  {count}: {ticker}: z-score = {z:.2f}")
                count += 1
            print()
