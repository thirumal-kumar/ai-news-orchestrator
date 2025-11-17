import requests
from bs4 import BeautifulSoup

url = "https://news.google.com/search?q=Delhi+air+pollution&hl=en-IN&gl=IN&ceid=IN:en"

resp = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36"
    },
    timeout=15
)

print("Status code:", resp.status_code)
print("First 2000 chars of HTML:\n")
print(resp.text[:2000])

soup = BeautifulSoup(resp.text, "html.parser")

links = soup.find_all("a")
print("\nNumber of <a> tags found:", len(links))

print("\nFirst 10 link hrefs:")
for a in links[:10]:
    print(a.get("href"))
