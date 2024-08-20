from src.utils import start_driver, save_to_csv
from selenium_driverless.types.by import By
from alive_progress import alive_bar
import os
import sys
import argparse
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parser = argparse.ArgumentParser(description="Substack scraper")
parser.add_argument("-u", "--url", type=str, help="post's url", default="https://goldenwitch.substack.com/p/3-reasons-to-love-anime")
args = parser.parse_args()

# You can set the creator url here if you don't want to use command line arguments
# args.url = "https://goldenwitch.substack.com/p/3-reasons-to-love-anime"


async def safe_get_element_text(driver, selector, post_attr, default=None):
    try:
        element = await driver.find_element(By.CSS_SELECTOR, selector)
        element_text = await element.get_attribute("textContent")
        return element_text.strip()
    except Exception:
        if post_attr == "post_date":
            try:
                element = await driver.find_element(By.CSS_SELECTOR, "div.post-header > div > div > div > div > div + div")
                element_text = await element.get_attribute("textContent")
                return element_text.strip()
            except Exception:
                return default
        elif post_attr == "post_author":
            try:
                element = await driver.find_element(By.CSS_SELECTOR, "div.post-header > div > div > div > div > div > div[class*='profile']")
                element_text = await element.get_attribute("textContent")
                return element_text.strip()
            except Exception:
                return default
        else:
            return default


async def main():
    driver = await start_driver()

    await driver.get(args.url)

    with alive_bar(8, bar="smooth", spinner="dots", title="Getting post data ") as bar:
        post_title = await safe_get_element_text(driver, "h1[class*=post-title]", "post_title", default=" ")
        bar()
        post_subtitle = await safe_get_element_text(driver, "h3[class*=subtitle]", "post_subtitle", default=" ")
        bar()
        post_date = await safe_get_element_text(driver, "div.post-header > div > div > div > div + div > div + div", "post_date", default=" ")
        bar()
        post_author = await safe_get_element_text(driver, "div.post-header > div > div > div > div + div > div > div", "post_author", default=" ")
        bar()
        post_likes = await safe_get_element_text(driver, "div[class*='like-button-container'] div.label", "post_likes", default="0")
        bar()
        post_comments = await safe_get_element_text(driver, "div.post-header a[href*='/comments'] div.label", "post_comments", default="0")
        bar()
        post_url = args.url
        bar()
        post_content = await safe_get_element_text(driver, "div.available-content", "post_content", default=" ")
        bar()

    await driver.quit()

    data = {
        "post-title": post_title,
        "post-subtitle": post_subtitle,
        "post-date": post_date,
        "post-author": post_author,
        "post-likes": post_likes,
        "post-comments": post_comments,
        "post-url": post_url,
        "post-content": post_content,
    }

    save_to_csv(data, "src/get_post/post.csv", data.keys(), "Post")


asyncio.run(main())
