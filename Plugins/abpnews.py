from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup

# Function to fetch BBC news RSS feed
def fetch_abpnews():
    try:
        # Fetching the BBC news RSS feed
        url = "https://news.abplive.com/home/feed"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'xml')
        
        # Find the title, description, and image URL from the RSS feed
        news = []
        for item in soup.find_all('item'):
            title = item.find('title').text
            image_tag = item.find('media:thumbnail')
            image_url = image_tag.get('url') if image_tag else None
            news.append((title, image_url))
        
        return news
    except Exception as e:
        print(f"Error fetching BBC news: {e}")
        return []

# Create the bot command to fetch the first 5 news articles
@Client.on_message(filters.command("abp"))
async def abpp(client, message):
    news = fetch_abpnews()
    for i in range(min(5, len(news))):  # Ensure we don't exceed the list length
        title, image_url = news[i]
        if image_url:
            await client.send_photo(
                message.chat.id,
                image_url,
                caption=f"<b>{title}</b>"
            )
        else:
            await client.send_message(
                message.chat.id,
                f"<b>{title}</b>"
            )