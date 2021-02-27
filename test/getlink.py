from re import search
from bs4 import BeautifulSoup
import requests, os, re, seltest2
testMatchID = '239922'
matchLinkPattern = re.compile(r".+?(?=full-scorecard)") #match is the link without 'full-scorecard'

def getMatch():
    res = requests.get(f"https://www.google.com/search?q={testMatchID}%20site:espncricinfo.com").text
    soup = BeautifulSoup(res, 'lxml')
    resultLinks = soup.findAll('a', href=True)
    for r in resultLinks:
        link_ = r.get('href')
        if testMatchID in link_ and '/full-scorecard' in link_:
            link_ = link_.replace("/url?q=", "")
            link_ = matchLinkPattern.match(link_)
            link_ = link_.group(0)
            seltest2.MyBot(link_, testMatchID)

getMatch()


def getMatchList():
    for filename in os.listdir('data/tests'):
        print(filename)

# indPlayer_link = f"https://search.espncricinfo.com/ci/content/site/search.html?search={nonSplit[-1]}"
# html_request = requests.get(indPlayer_link).text
# soup = BeautifulSoup(html_request, 'lxml')
# playerSearch = soup.findAll('h3', class_='name link-cta')