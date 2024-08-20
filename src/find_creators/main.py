from src.utils import start_driver, get_creator_page_infos, get_headers_and_pubid, save_to_csv
from selenium_driverless.types.by import By
from urllib.parse import urlparse, quote
from alive_progress import alive_bar
import os
import sys
import asyncio
import argparse
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parser = argparse.ArgumentParser(description="Substack scraper")
parser.add_argument("-k", "--keyword", type=str, help="Search keyword")
parser.add_argument("-t", "--type", type=str, help="Search type", default="publication")
parser.add_argument("-r", "--range", type=int, help="Increase this value to capture more creators", default=5)
args = parser.parse_args()

# You can set keyword and type here if you don't want to use command line arguments
# args.keyword = "jujutsu kaisen"
# args.type = "publication"
# args.range = 15


async def get_creators_data(driver, creators_page_links):
    creators_data = []
    with alive_bar(len(creators_page_links), bar="smooth", spinner="dots", title="Getting creators data ") as bar:
        for creator_page_link in creators_page_links:
            try:
                name, description, subscribers, link, blog_url = await get_creator_page_infos(driver, creator_page_link)
                creator_data = {"name": name, "description": description, "subscribers": subscribers, "link": link}
                publication_id, headers, domain = await get_headers_and_pubid(driver, blog_url, args.keyword)
                search_posts_api_url = f"https://{domain}/api/v1/post/search?query={quote(args.keyword)}&focusedPublicationId={publication_id}&page=0&numberFocused=10"
                response = requests.get(search_posts_api_url, headers=headers)

                if response.status_code == 200:
                    posts = response.json()["results"]
                    urls = [post["canonical_url"] for post in posts]
                    post_count = 0
                    for url in urls:
                        post_count += 1
                        creator_data[f"post{post_count}"] = url
                        if post_count > 4:
                            break

                creators_data.append(creator_data)
                bar()
            except Exception:
                continue
    print("✅ Got all creators data.")
    return creators_data


async def get_creators_page_links(driver, about_page_links):
    links = []
    with alive_bar(len(about_page_links), bar="smooth", spinner="dots", title="Getting creators page urls ") as bar:
        for about_page_link in about_page_links:
            await driver.get(about_page_link, wait_load=True)
            await driver.sleep(0.5)
            creators_links_elements = await driver.find_elements(By.CSS_SELECTOR, "div.content-person a")
            creators_links = [await element.get_attribute("href") for element in creators_links_elements]
            [links.append(link) for link in creators_links if link not in links]
            bar()
    print("✅ Got all creators urls.")
    return links


async def find_creators_by_posts(driver):
    await driver.get(
        f"https://substack.com/search/{args.keyword}?utm_source=global-search&searching=all_posts",
        wait_load=True,
    )
    await driver.sleep(0.5)

    for i in range(args.range):  # Increase this number to get more creators
        await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        await driver.sleep(1)

    blog_links_elements = await driver.find_elements(By.CSS_SELECTOR, "div.pub-name a")
    blog_links = [await element.get_attribute("href") for element in blog_links_elements]
    about_page_links = [f"{link}about" for link in blog_links]

    creators_page_links = await get_creators_page_links(driver, about_page_links)
    creators_data = await get_creators_data(driver, creators_page_links)
    return creators_data


async def find_creators_by_publications(driver):
    await driver.get(
        f"https://substack.com/search/{args.keyword}?utm_source=global-search&searching=publication",
        wait_load=True,
    )
    await driver.sleep(0.5)

    for i in range(args.range):  # Increase this number to get more creators
        await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        await driver.sleep(1)

    blog_urls_elements = await driver.find_elements(By.CSS_SELECTOR, 'a[href*="/?utm_source=substack"]')
    blog_urls = [await element.get_attribute("href") for element in blog_urls_elements]
    about_page_links = []

    for blog_url in blog_urls:
        parsed_url = urlparse(blog_url)
        domain = parsed_url.netloc
        about_page_links.append(f"https://{domain}/about")

    creators_page_links = await get_creators_page_links(driver, about_page_links)
    creators_data = await get_creators_data(driver, creators_page_links)
    return creators_data


async def main():
    if args.type not in ["post", "publication"]:
        print(f'Invalid search type: {args.type}. You must pass "post" or "publication"')
        raise ValueError(
            "Invalid value",
            f"Invalid type: {args.type}. You must pass, post or publication",
        )

    if not args.keyword:
        print("You must pass a keyword")
        raise ValueError("Invalid value", "You must pass a keyword")

    driver = await start_driver()

    if args.type == "post":
        data = await find_creators_by_posts(driver)
    elif args.type == "publication":
        data = await find_creators_by_publications(driver)

    await driver.quit()

    headers = [
        "name",
        "description",
        "subscribers",
        "link",
        "post1",
        "post2",
        "post3",
        "post4",
        "post5",
    ]

    save_to_csv(data, "src/find_creators/creators.csv", headers, "Creators")


asyncio.run(main())
