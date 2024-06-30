import feedparser
import requests
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
    try:
        with open("README.md", "r") as file:
            readme_content = file.readlines()

        start_index = readme_content.index("<!-- BLOG-POST-THUMBNAILS:START -->\n")
        end_index = readme_content.index("<!-- BLOG-POST-THUMBNAILS:END -->\n")

        new_content = ["<!-- BLOG-POST-THUMBNAILS:START -->\n"]
        new_content.append('<div style="display:inline; overflow: auto; white-space: nowrap; padding: 10px; gap: 10px;">\n')

        for post in posts:
            new_content.append(
                f'  <a href="{post["link"]}" style="text-decoration: none; color: inherit; margin: 15px; position: relative; flex: 0 0 auto; width: 100px; height: 150px;">\n'
                f'    <img src="{post["thumbnail"]}" alt="{post["title"]}" style="width: 100px; height: 150px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: transform 0.2s; padding: 2%;">\n'
                f'  </a>\n'
            )

        new_content.append('</div>\n')
        # new_content.append('<script>\n')
        # new_content.append('  document.querySelectorAll(".thumbnails a").forEach(a => {\n')
        # new_content.append('    a.addEventListener("mouseover", () => {\n')
        # new_content.append('      a.querySelector("img").style.transform = "scale(1.05)";\n')
        # new_content.append('      a.querySelector("div").style.opacity = "1";\n')
        # new_content.append('    });\n')
        # new_content.append('    a.addEventListener("mouseout", () => {\n')
        # new_content.append('      a.querySelector("img").style.transform = "scale(1)";\n')
        # new_content.append('      a.querySelector("div").style.opacity = "0";\n')
        # new_content.append('    });\n')
        # new_content.append('  });\n')
        # new_content.append('</script>\n')
        new_content.append("<!-- BLOG-POST-THUMBNAILS:END -->\n")

        readme_content[start_index:end_index + 1] = new_content

        with open("README.md", "w") as file:
            file.writelines(readme_content)

    except ValueError:
        print("Placeholder comments not found in README.md. Please ensure they are correctly placed.")

def main():
    medium_username = os.getenv("MEDIUM_USERNAME")
    feed = fetch_medium_feed(medium_username)
    posts = []

    for entry in feed.entries[:5]:  # Get the latest 5 posts
        post = {
            "title": entry.title,
            "link": entry.link,
            "thumbnail": extract_thumbnail(entry.link)
        }
        if post.get('thumbnail',None):
            posts.append(post)

    update_readme(posts)

if __name__ == "__main__":
    main()
