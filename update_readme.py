import feedparser
import requests
from bs4 import BeautifulSoup
import os
import requests
import json

# Funtion to check valid URL
def is_url_valid(url):
    response = requests.head(url)
    return response.status_code == 200

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

# Funtion to fetch languages used in my all repos
def fetch_languages(username):
    url = f"https://api.github.com/users/{username}/repos"
    repos = requests.get(url).json()
    languages = {}
    
    for repo in repos:
        if not repo['fork']:
            lang_url = repo['languages_url']
            repo_langs = requests.get(lang_url).json()
            for lang in repo_langs:
                if lang in languages:
                    languages[lang] += repo_langs[lang]
                else:
                    languages[lang] = repo_langs[lang]
    
    return languages

# Funtion to create badges of language
def create_language_logos(languages):
    github_explore_base_url = "https://raw.githubusercontent.com/github/explore/main/topics"
    default_logo_url = "https://via.placeholder.com/40?text=?"

    logos = []
    for lang in languages:
        logo_url = f"{github_explore_base_url}/{lang.lower()}/{lang.lower()}.png"
        if not is_url_valid(logo_url):
            logo_url = default_logo_url
        logos.append(f'<img src="{logo_url}" alt="{lang}" width="40" height="40" style="margin:20px; border-radius: 40% " />')
    return ' '.join(logos)

# Fetch languages and create badges
username = "dicusa"
languages = fetch_languages(username)
language_badges = create_language_logos(languages)

# Function to update the README.md file
def update_readme(posts):
    try:
        with open("README.md", "r") as file:
            readme_content = file.readlines()

        start_index = readme_content.index("<!-- BLOG-POST-THUMBNAILS:START -->\n")
        end_index = readme_content.index("<!-- BLOG-POST-THUMBNAILS:END -->\n")

        new_content = ["<!-- BLOG-POST-THUMBNAILS:START -->\n"]
        new_content.append('<table style="border-spacing: 0; border-collapse: separate;"><thead><tr>\n')

        for post in posts:
            new_content.append(
                f'  <th style="justify-content: space-between;">\n'
                f'    <a href="{post["link"]}" style="height:160px; width:130px">\n'
                f'      <img src="{post["thumbnail"]}" alt="" >\n'
                f'    </a>\n'
                f'<span>"{post["title"][:30]}"... '
                f'  </span></th>\n'
            )

        new_content.append('</tr></thead></table>\n')
        
        new_content.append("<!-- BLOG-POST-THUMBNAILS:END -->\n")

        readme_content[start_index:end_index + 1] = new_content

        lang_start_index = readme_content.index("<!-- LANGUAGES-USED-START -->\n")
        lang_end_index = readme_content.index("<!-- LANGUAGES-USED-END -->\n")
        
        new_content = ["<!-- LANGUAGES-USED-START -->\n"]
        new_content.append(f'{language_badges}\n')
        new_content.append("<!-- LANGUAGES-USED-END -->\n")
        readme_content[lang_start_index:lang_end_index+1] = new_content

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
