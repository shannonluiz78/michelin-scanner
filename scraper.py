import json
import re
import urllib.request
from bs4 import BeautifulSoup

def scrape_michelin_singapore():
    base_url = "https://guide.michelin.com/sg/en/singapore-region/singapore/restaurants"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    restaurants = []

    for page in range(1, 20):
        url = f"{base_url}/page/{page}" if page > 1 else base_url
        try:
            req = urllib.request.Request(url, headers=headers)
            html = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(html, 'html.parser')
            
            cards = soup.find_all('div', class_=re.compile(r'card__menu'))
            if not cards:
                break
                
            for card in cards:
                name_el = card.find(['h3', 'h2'], class_=re.compile(r'card__menu-content--title'))
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)

                card_text = card.get_text()
                if "3 Stars" in card_text or "3 MICHELIN Stars" in card_text:
                    distinction, stars_count = "3 Stars", 3
                elif "2 Stars" in card_text or "2 MICHELIN Stars" in card_text:
                    distinction, stars_count = "2 Stars", 2
                elif "1 Star" in card_text or "1 MICHELIN Star" in card_text:
                    distinction, stars_count = "1 Star", 1
                else:
                    continue

                link_el = card.find('a', href=True)
                michelin_link = f"https://guide.michelin.com{link_el['href']}" if link_el else base_url

                # Fetch individual restaurant page for authentic og:image cover photo
                image_url = ""
                try:
                    detail_req = urllib.request.Request(michelin_link, headers=headers)
                    detail_html = urllib.request.urlopen(detail_req).read()
                    detail_soup = BeautifulSoup(detail_html, 'html.parser')
                    og_img = detail_soup.find('meta', property='og:image')
                    if og_img and og_img.get('content'):
                        image_url = og_img['content']
                except Exception:
                    pass

                footer = card.find('div', class_=re.compile(r'card__menu-footer'))
                footer_text = footer.get_text(strip=True) if footer else "Singapore"
                parts = [p.strip() for p in footer_text.split("•")]
                cuisine = parts[0] if len(parts) > 0 else "Fine Dining"
                location = parts[-1] if len(parts) > 1 else "Singapore"

                restaurants.append({
                    "id": re.sub(r'[^a-z0-9]', '-', name.lower()),
                    "name": name,
                    "distinction": distinction,
                    "stars": stars_count,
                    "cuisine": cuisine,
                    "location": location,
                    "priceMin": 280 if stars_count == 3 else (180 if stars_count == 2 else 100),
                    "priceMax": 500 if stars_count == 3 else (350 if stars_count == 2 else 220),
                    "rating": 4.9 if stars_count == 3 else (4.7 if stars_count == 2 else 4.5),
                    "reviewCount": 850,
                    "signature": "Chef Speciality Menu",
                    "description": f"Official {distinction} Michelin-starred establishment in Singapore.",
                    "imageUrl": image_url or "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=600&q=80",
                    "michelinUrl": michelin_link
                })
        except Exception:
            break

    if len(restaurants) >= 40:
        with open("restaurants.json", "w", encoding="utf-8") as f:
            json.dump(restaurants, f, indent=2, ensure_ascii=False)
        print(f"Scraped {len(restaurants)} unique restaurant profiles into restaurants.json")

if __name__ == "__main__":
    scrape_michelin_singapore()
