import requests
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup

# Website and User-Agent
SITE_URL = 'https://www.thehindubusinessline.com'
ROBOTS_URL = SITE_URL + '/robots.txt'
USER_AGENT = 'Mozilla/5.0 (compatible; RespectfulBot/1.0)'

# Parse robots.txt
rp = RobotFileParser()
rp.set_url(ROBOTS_URL)
rp.read()

target_url = SITE_URL + '/economy/'
if rp.can_fetch(USER_AGENT, target_url):
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Update this section based on page structure
    articles = soup.find_all('a', {'class': 'story-card75x1-text'})

    for article in articles:
        title = article.get_text(strip=True)
        link = article['href']
        print(f'Title: {title}\nLink: {link}\n')
else:
    print('Access to this section is disallowed by robots.txt. No scraping performed.')
