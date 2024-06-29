import feedparser
import requests
import re
from bs4 import BeautifulSoup
import os

# Function to fetch the Medium feed
def fetch_medium_feed(username):
    feed_url = f"https://medium.com/feed/@{username}"
    return feedparser.parse(feed_url)

# Function to extract the thumbnail URL from a Medium post
def extract_thumbnail(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    og_image = soup.find('meta', property='og:image')
    if og_image:
        return og_image['content']
    return None

# Function to update the README.md file
def update_readme(posts):
    with open("README.md", "r") as file:
        readme_content = file.readlines()

    start_index = readme_content.index("<!-- BLOG-POST-THUMBNAILS:START -->\n")
    end_index = readme_content.index("<!-- BLOG-POST-THUMBNAILS:END -->\n")

    new_content = ["<!-- BLOG-POST-THUMBNAILS:START -->\n"]
    new_content.append('<div style="display: flex; overflow-x: scroll;">\n')

    for post in posts:
        new_content.append(
            f'  <a href="{post["link"]}">\n'
            f'    <img src="{post["thumbnail"]}" alt="{post["title"]}" style="width: 150px; height: 150px; margin-right: 10px;">\n'
            f'  </a>\n'
        )

    new_content.append('</div>\n')
    new_content.append("<!-- BLOG-POST-THUMBNAILS:END -->\n")

    readme_content[start_index:end_index + 1] = new_content

    with open("README.md", "w") as file:
        file.writelines(readme_content)

def main():
    medium_username = '@jain.yash1909'
    feed = fetch_medium_feed(medium_username)
    posts = []

    for entry in feed.entries[:5]:  # Get the latest 5 posts
        post = {
            "title": entry.title,
            "link": entry.link,
            "thumbnail": extract_thumbnail(entry.link)
        }
        posts.append(post)

    update_readme(posts)

if __name__ == "__main__":
    main()
