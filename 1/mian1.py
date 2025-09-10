import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}
response = requests.get("https://jwc.scau.edu.cn/xl/list.psp", headers=headers)
# response = requests.get("https://www.douyin.com/", headers=headers)
content = response.text
soup = BeautifulSoup(content, "html.parser")
# all_data = soup.find_all("span", attrs={"class": "news_meta"})
all_data = soup.find_all("span", attrs={"class": "news_title"})
for data in all_data:
    link = data.find("a")
    print(link.string)

