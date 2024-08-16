from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from urllib.parse import urlparse, quote
import json
import asyncio
import argparse
import hrequests

parser = argparse.ArgumentParser(description='Substack scraper')
parser.add_argument('-kw', '--keyword', type=str, help='Search keyword')
parser.add_argument('-t', '--type', type=str, help='Search type')
args = parser.parse_args()

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

async def get_creators_data(driver, creators_page_links):
  creators_data = []  

  for creator_page_link in creators_page_links[0:1]:
    await driver.get(creator_page_link, wait_load=True)
    await driver.sleep(0.5) 

    creator_data = {
      'name': (await (await driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] + script + div > div > div h3')).text).replace('\xa0', ''),
      'description': (await (await driver.find_element(By.CSS_SELECTOR, 'div[role="dialog"] + script + div > div > div > div + div > div > span')).text).replace('\n', ' '),
      'subscribers': await (await driver.find_element(By.CSS_SELECTOR, 'a[href*="subscribers"] div')).text,
      'link': creator_page_link
    }

    blog_url = await (await driver.find_element(By.CSS_SELECTOR, 'a[href*="/?utm_source=substack&"]')).get_attribute("href")
    parsed_url = urlparse(blog_url)
    domain = parsed_url.netloc

    await driver.get(blog_url, wait_load=True)
    await driver.sleep(0.5)

    button_maybe_later = await driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="maybeLater"]')

    if button_maybe_later:
      await button_maybe_later[0].click()

    cookies = await driver.get_cookies()
    formatted_cookies = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])    

    headers = {
      'Authority': domain,
      'Method': 'GET',
      'Path': f'/api/v1/post/search?query={args.keyword}&focusedPublicationId=274055&page=0&numberFocused=10',
      'Scheme': 'https',
      'Accept': '*/*',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
      'Cache-Control': 'max-age=0',
      'Cookie': formatted_cookies,
      'If-None-Match': 'W/"cecd-3F6FnH66WPUwFW90m1k7Jw+sFgc"',
      'Priority': 'u=1, i',
      'Referer': blog_url,
      'Sec-Ch-Ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
      'Sec-Ch-Ua-Mobile': '?0',
      'Sec-Ch-Ua-Platform': '"Windows"',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    publication_id = await driver.execute_script("return window._analyticsConfig.properties.publication_id")    

    response = hrequests.get(f'https://{domain}/api/v1/post/search?query={quote(args.keyword)}&focusedPublicationId={publication_id}&page=0&numberFocused=10', headers=headers)
  
    if response.status_code == 200:
      posts = response.json()['results']
      urls = [post['canonical_url'] for post in posts]
      post_count = 0    
      for url in urls:
        post_count += 1
        creator_data[f'post{post_count}'] = url

    creators_data.append(creator_data)
  return creators_data

async def get_creators_page_links(driver, about_page_links):
  links = []
  for about_page_link in about_page_links[0:2]:
    await driver.get(about_page_link, wait_load=True)
    await driver.sleep(0.5)
    creators_links_elements = await driver.find_elements(By.CSS_SELECTOR, 'div.content-person a')
    creators_links = [await element.get_attribute('href') for element in creators_links_elements]
    [links.append(link) for link in creators_links if link not in links]
  return links

async def find_creators_by_posts(driver):
  await driver.get(f"https://substack.com/search/{args.keyword}?utm_source=global-search&searching=all_posts", wait_load=True)
  await driver.sleep(0.5)

  for i in range(1):
    await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    await driver.sleep(1)

  blog_links_elements = await driver.find_elements(By.CSS_SELECTOR, 'div.pub-name a')
  blog_links = [await element.get_attribute('href') for element in blog_links_elements]
  about_page_links = [f'{link}about' for link in blog_links]

  creators_page_links = await get_creators_page_links(driver, about_page_links)
  creators_data = await get_creators_data(driver, creators_page_links)
  return creators_data


async def main():
  if args.type not in ['post', 'publication']:
    print(f'Invalid type: {args.type}. You must pass, post or publication')
    raise ValueError('Invalid value', f'Invalid type: {args.type}. You must pass, post or publication')

  driver = await start_driver()
  
  if (args.type == 'post'):
    data = await find_creators_by_posts(driver)

  print(data)
  



asyncio.run(main())

