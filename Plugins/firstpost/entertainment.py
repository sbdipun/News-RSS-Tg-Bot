import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters


# Fetch the Top Stories 
def fetch_ent():
    try:
        url = "https://www.firstpost.com/commonfeeds/v1/mfp/rss/entertainment.xml"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'xml')

        # Find the title, description, and image URL from the RSS feed
        news = []
        for item in soup.find_all('item'):
            title = item.find('title').text
            description_tag = item.find('description')
            description = description_tag.text if description_tag else None
            image_tag = item.find('media:content')
            image_url = image_tag.get('url') if image_tag else None
            news.append((title, description, image_url))
        
        return news
    except Exception as e:
        print(f"Error fetching Times Of India News: {e}")
        return []
    
# Create the bot command to fetch the first 5 news articles
@Client.on_message(filters.command("firstpostent"))
async def bbc(client, message):
    news = fetch_ent()
    for i in range(min(5, len(news))):  # Ensure we don't exceed the list length
        title, description, image_url = news[i]
        if image_url:
            await client.send_photo(
                message.chat.id,
                image_url,
                caption=f"<b>{title}\n\n{description}</b>"
            )
        else:
            await client.send_message(
                message.chat.id,
                f"<b>{title}\n\n{description}</b>"
            )
