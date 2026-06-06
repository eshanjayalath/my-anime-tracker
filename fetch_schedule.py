import requests
import json
from datetime import datetime

def fetch_anime_schedule():
    # Fetch airing anime schedule from Jikan API (MyAnimeList wrapper)
    url = "https://api.jikan.moe/v4/schedules"
    try:
        response = requests.get(url, params={"limit": 20})
        if response.status_code == 200:
            data = response.json().get('data', [])
            schedule = []
            for item in data:
                schedule.append({
                    "title": item['title_english'] or item['title'],
                    "type": "Anime",
                    "time": item.get('broadcast', {}).get('time', 'N/A'),
                    "day": item.get('broadcast', {}).get('day', 'N/A'),
                    "image": item['images']['jpg']['image_url']
                })
            return schedule
    except Exception as e:
        print(f"Error fetching anime: {e}")
    return []

def fetch_manga_schedule():
    # Fetch trending/releasing manga from AniList (GraphQL)
    url = 'https://graphql.anilist.co'
    query = '''
    query {
      Page(page: 1, perPage: 20) {
        media(type: MANGA, status: RELEASING, sort: TRENDING_DESC) {
          title { romaji english }
          coverImage { large }
          nextAiringEpisode { airingAt timeUntilAiring }
        }
      }
    }
    '''
    try:
        response = requests.post(url, json={'query': query})
        if response.status_code == 200:
            items = response.json()['data']['Page']['media']
            schedule = []
            for item in items:
                schedule.append({
                    "title": item['title']['english'] or item['title']['romaji'],
                    "type": "Manga",
                    "image": item['coverImage']['large'],
                    # Dummy entry if next chapter date isn't explicitly exposed by API
                    "day": "Weekly Updates" 
                })
            return schedule
    except Exception as e:
        print(f"Error fetching manga: {e}")
    return []

if __name__ == "__main__":
    combined_data = {
        "last_updated": datetime.utcnow().isoformat(),
        "releases": fetch_anime_schedule() + fetch_manga_schedule()
    }
    
    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4, ensure_ascii=False)
    print("Schedule updated successfully!")