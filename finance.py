import yfinance as yf
from datetime import datetime, timedelta
from lxml import html

N = 30


def scrape_hang_seng_codes():
    # Open local HTML file you downloaded as test.html
    with open("hsi.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Parse the HTML content from the file
    tree = html.fromstring(content)

    codes = []
    for i in range(1, 90):
        xpath_code = f'//*[@id="tblTS2"]/tbody/tr[{i}]/td[1]/div[2]/div[1]/a'
        elements = tree.xpath(xpath_code)
        if elements:
            code = elements[0].text.strip()

            # print(f"Row {i}: found code {elements[0].text.strip()}")
            codes.append(code[1:])
        else:
            print(f"Row {i}: no code found")

    return codes


if __name__ == "__main__":
    # Define the date range to fetch data: last 45 calendar days to cover 30 trading days approx
    end_date = datetime.today()
    start_date = end_date - timedelta(days=45)

    # hang_seng_tickers = scrape_hang_seng_codes()
    # print(hang_seng_tickers)

    hang_seng_tickers = [
        "0001.HK",
        "0002.HK",
        "0003.HK",
        "0005.HK",
        "0006.HK",
        "0011.HK",
        "0012.HK",
        "0016.HK",
        "0027.HK",
        "0066.HK",
        "0101.HK",
        "0175.HK",
        "0241.HK",
        "0267.HK",
        "0285.HK",
        "0288.HK",
        "0291.HK",
        "0300.HK",
        "0316.HK",
        "0322.HK",
        "0386.HK",
        "0388.HK",
        "0669.HK",
        "0688.HK",
        "0700.HK",
        "0728.HK",
        "0762.HK",
        "0823.HK",
        "0836.HK",
        "0857.HK",
        "0868.HK",
        "0881.HK",
        "0883.HK",
        "0939.HK",
        "0941.HK",
        "0960.HK",
        "0968.HK",
        "0981.HK",
        "0992.HK",
        "1024.HK",
        "1038.HK",
        "1044.HK",
        "1088.HK",
        "1093.HK",
        "1099.HK",
        "1109.HK",
        "1113.HK",
        "1177.HK",
        "1209.HK",
        "1211.HK",
        "1299.HK",
        "1378.HK",
        "1398.HK",
        "1801.HK",
        "1810.HK",
        "1876.HK",
        "1928.HK",
        "1929.HK",
        "1997.HK",
        "2015.HK",
        "2020.HK",
        "2057.HK",
        "2269.HK",
        "2313.HK",
        "2318.HK",
        "2319.HK",
        "2331.HK",
        "2359.HK",
        "2382.HK",
        "2388.HK",
        "2618.HK",
        "2628.HK",
        "2688.HK",
        "2899.HK",
        "3690.HK",
        "3692.HK",
        "3968.HK",
        "3988.HK",
        "6618.HK",
        "6690.HK",
        "6862.HK",
        "9618.HK",
        "9633.HK",
        "9888.HK",
        "9901.HK",
        "9961.HK",
        "9988.HK",
        "9992.HK",
        "9999.HK",
    ]

    # custome list
    # hang_seng_tickers = [
    #     "9988.HK",
    #     "0175.HK",
    #     "9626.HK",
    #     "2018.HK",
    #     "1024.HK",
    #     "2318.HK",
    #     "0386.HK",
    #     "0857.HK",
    #     "0883.HK",
    # ]

    # Dictionary to store results: {ticker: (name, latest_z_score)}
    z_scores = {}

    count = 1

    for ticker in hang_seng_tickers:
        df = yf.download(
            ticker,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=False,
        )

        print(f"{count}: Finish Downloading {ticker}")
        count += 1
        # Take last 30 rows of data (last 30 trading days)
        df = df.tail(N)

        if df.empty or "Close" not in df.columns or len(df) < 20:
            print(f"Skipping {ticker}: insufficient data")
            continue

        # Calculate rolling mean and std dev for the 30 days (simple mean and std here)
        mean = df["Close"].mean()
        std = df["Close"].std()

        # Calculate z-score for the latest day
        latest_close = df["Close"].iloc[-1]
        latest_z = (latest_close - mean) / std

        # Get company name from ticker info (handle potential errors)
        try:
            info = yf.Ticker(ticker).info
            name = info.get("longName", ticker)
        except Exception:
            name = ticker

        z_scores[ticker] = (name, latest_z)

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

    for ticker, (name, z) in z_scores.items():
        z = z.iloc[0]
        if z < -2:
            categories[cat_a].append((ticker, name, z))
        elif -2 <= z < 0:
            categories[cat_b].append((ticker, name, z))
        elif 0 <= z < 2:
            categories[cat_c].append((ticker, name, z))
        else:  # z >= 2
            categories[cat_d].append((ticker, name, z))

    # Print summary
    for cat, stocks in categories.items():
        stocks.sort(key=lambda x: x[2])
        print(f"Category: {cat} (Total {len(stocks)})")
        count = 1
        for ticker, name, z in stocks:
            print(f"  {count}: {ticker} ({name}): z-score = {z:.2f}")
            count += 1
        print()
