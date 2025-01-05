import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters


# Creating the function to retrive the News rss from times of india
def fetch_indtoday():
    try:
        url = "https://www.indiatoday.in/rss/home"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'xml')

        # Find the title, description, and image URL from the RSS feed
        news = []
        # Find the title, description, and image URL from the RSS feed
        news = []
        for item in soup.find_all('item'):
            title = item.find('title').text
            
            # Extract description (which contains HTML-like content)
            description = item.find('description').text
            
            # Parse the description to extract image URL and text
            description_soup = BeautifulSoup(description, 'html.parser')
            
            # Extract image URL from <img> tag
            img_tag = description_soup.find('img')
            image_url = img_tag.get('src') if img_tag else None
            
            news.append((title, image_url))
        
        
        return news
    except Exception as e:
        print(f"Error fetching Times Of India News: {e}")
        return []
    
# Create the bot command to fetch the first 5 news articles
@Client.on_message(filters.command("indtoday"))
async def bbc(client, message):
    news = fetch_indtoday()
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
