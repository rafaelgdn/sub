from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from urllib.parse import urlparse
import csv


async def start_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")   # uncomment this line to run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=BlockInsecurePrivateNetworkRequests")
    options.add_argument("--disable-features=OutOfBlinkCors")
    options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-features=CrossSiteDocumentBlockingIfIsolating,CrossSiteDocumentBlockingAlways")
    options.add_argument("--disable-features=ImprovedCookieControls,LaxSameSiteCookies,SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-features=SameSiteDefaultChecksMethodRigorously")
    driver = await webdriver.Chrome(options=options)
    return driver


async def get_creator_page_infos(driver, url):
    await driver.get(url, wait_load=True)
    await driver.sleep(0.5)
    name = (await (await driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] + script + div > div > div h3')).text).replace("\xa0", "")
    description = (await (await driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] + script + div > div > div > div + div > div > span')).text).replace("\n", " ")
    subscribers = await (await driver.find_element(By.CSS_SELECTOR, 'a[href*="subscribers"] div')).text
    link = url
    blog_url = await (await driver.find_element(By.CSS_SELECTOR, 'a[href*="/?utm_source=substack&"]')).get_attribute("href")
    return name, description, subscribers, link, blog_url


async def get_headers_and_pubid(driver, blog_url, keyword=None):
    parsed_url = urlparse(blog_url)
    domain = parsed_url.netloc
    await driver.get(blog_url, wait_load=True)
    await driver.sleep(0.5)
    cookies = await driver.get_cookies()
    formatted_cookies = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    headers = {
        "Authority": domain,
        "Method": "GET",
        "Scheme": "https",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
        "Cache-Control": "max-age=0",
        "Cookie": formatted_cookies,
        "If-None-Match": 'W/"cecd-3F6FnH66WPUwFW90m1k7Jw+sFgc"',
        "Priority": "u=1, i",
        "Referer": blog_url,
        "Sec-Ch-Ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    }

    if keyword:
        headers["Path"] = f"/api/v1/post/search?query={keyword}&focusedPublicationId=274055&page=0&numberFocused=10"

    publication_id = await driver.execute_script("return window._analyticsConfig.properties.publication_id")
    return publication_id, headers, domain


def save_to_csv(data, filename, headers):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        if isinstance(data, dict):
            writer.writerow(data)
        elif isinstance(data, list):
            for row in data:
                if isinstance(row, dict):
                    writer.writerow(row)
                else:
                    print(f"Skipping invalid row: {row}")
        else:
            raise TypeError("Data must be a dictionary or a list of dictionaries")

    print(f"✅ Creator data successfully saved to {filename}")


# def save_to_csv(data, filename, headers):
#     file_exists = os.path.isfile(filename)
#     with open(filename, "a", newline="", encoding="utf-8") as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=headers)
#         if not file_exists:
#             writer.writeheader()
#         for row in data:
#             writer.writerow(row)
