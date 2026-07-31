import requests
from bs4 import BeautifulSoup

url = "https://www.blogdumoderateur.com/web/"
headers = {"User-Agent": "DataHarvest/1.0 (+contact@ipssi.fr)"}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

liens = soup.select("header.entry-header a")
for i, a in enumerate(liens):
    print(i, "-", a.get_text(strip=True)[:40])