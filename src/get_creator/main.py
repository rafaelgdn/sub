from src.utils import start_driver, get_creator_page_infos, get_headers_and_pubid, save_to_csv
from alive_progress import alive_bar
import os
import sys
import argparse
import asyncio
import hrequests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
parser = argparse.ArgumentParser(description="Substack scraper")
parser.add_argument("-u", "--url", type=str, help="creator's url", default="https://substack.com/@jonathanhaidt")
args = parser.parse_args()

# You can set the creator url here if you don't want to use command line arguments
# args.url = "https://substack.com/@jonathanhaidt"


async def main():
    if not args.url:
        print("You must pass a creator url")
        raise ValueError("Invalid value", "You must pass a creator url")

    driver = await start_driver()

    with alive_bar(8, bar="smooth", spinner="dots", title="Getting creator data ") as bar:
        name, description, subscribers, link, blog_url = await get_creator_page_infos(driver, args.url)
        creator_data = {"name": name, "description": description, "subscribers": subscribers, "link": link}
        publication_id, headers, domain = await get_headers_and_pubid(driver, blog_url)

        # Get the popular posts
        popular_posts_api_url = f"https://{domain}/api/v1/archive?sort=top&search=&offset=0&limit=12"
        popular_posts_response = hrequests.get(popular_posts_api_url, headers=headers)

        if popular_posts_response.status_code == 200:
            posts = popular_posts_response.json()
            popular_post_count = 0
            for post in posts:
                popular_post_count += 1
                creator_data[f"popular-post{popular_post_count}-url"] = post["canonical_url"]
                creator_data[f"popular-post{popular_post_count}-title"] = post["title"]
                creator_data[f"popular-post{popular_post_count}-description"] = post["description"]
                creator_data[f"popular-post{popular_post_count}-date"] = post["post_date"]
                bar()
                if popular_post_count > 3:
                    break

            # Get the latest posts
            latest_posts_api_url = f"https://{domain}/api/v1/archive?sort=new&search=&offset=0&limit=12"
            latest_posts_response = hrequests.get(latest_posts_api_url, headers=headers)

            if latest_posts_response.status_code == 200:
                posts = latest_posts_response.json()
                latest_post_count = 0
                for post in posts:
                    latest_post_count += 1
                    creator_data[f"latest-post{latest_post_count}-url"] = post["canonical_url"]
                    creator_data[f"latest-post{latest_post_count}-title"] = post["title"]
                    creator_data[f"latest-post{latest_post_count}-description"] = post["description"]
                    creator_data[f"latest-post{latest_post_count}-date"] = post["post_date"]
                    bar()
                    if latest_post_count > 3:
                        break

    await driver.quit()

    headers = [
        "name",
        "description",
        "subscribers",
        "link",
        "popular-post1-url",
        "popular-post1-title",
        "popular-post1-description",
        "popular-post1-date",
        "popular-post2-url",
        "popular-post2-title",
        "popular-post2-description",
        "popular-post2-date",
        "popular-post3-url",
        "popular-post3-title",
        "popular-post3-description",
        "popular-post3-date",
        "popular-post4-url",
        "popular-post4-title",
        "popular-post4-description",
        "popular-post4-date",
        "latest-post1-url",
        "latest-post1-title",
        "latest-post1-description",
        "latest-post1-date",
        "latest-post2-url",
        "latest-post2-title",
        "latest-post2-description",
        "latest-post2-date",
        "latest-post3-url",
        "latest-post3-title",
        "latest-post3-description",
        "latest-post3-date",
        "latest-post4-url",
        "latest-post4-title",
        "latest-post4-description",
        "latest-post4-date",
    ]

    save_to_csv(creator_data, "src/get_creator/creator.csv", headers)


asyncio.run(main())
