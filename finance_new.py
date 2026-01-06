import requests
from selenium import webdriver
import bs4

N = 20


def test():
    driver = webdriver.Chrome()
    driver.get("https://www.google.com")
    return driver.title == "Google"


if __name__ == "__main__":
    url = "https://hk.finance.yahoo.com/quote/0001.HK/history/"
    # print(test())
    driver = webdriver.Chrome()
    driver.get(url)
    # search with xpath
    # //*[@id="main-content-wrapper"]/div[1]/div[3]/table/tbody/tr[1]/td[6]
    # //*[@id="main-content-wrapper"]/div[1]/div[3]/table/tbody/tr[2]/td[6]
    print(driver.title)
    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    for i in range(1, N + 1):
        xpath = (
            f'//*[@id="main-content-wrapper"]/div[1]/div[3]/table/tbody/tr[{i}]/td[6]'
        )
        print(1)
        element = driver.find_element("xpath", xpath)
        print(2)
        print(element.text)
        print(3)
    driver.quit()
