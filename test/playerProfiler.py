import yaml
from bs4 import BeautifulSoup
import requests
import re
import infoadd

playerIDPattern = re.compile(r"(\/.+?(?=\/)){3}\/(.+?(?=\.html))") #group2 - playerID
playerBirthPattern = re.compile(r"(.+?(?=\s))(.+?(?=,)),\s(.+?(?=,))") #group1 - month, #group2 - date, #group3 - year
noMiddlePattern = re.compile(r"(.+?(?=,)),\s(.+)") #group1 - first, #group2 - last

localPlayerList = {}
trackerListBatter = {}
trackerListNonstriker = {}
trackerListBowler = {}

def process(matchId):
    global data

    def playerProcessing(indPlayer, indPlayer_link):
        global localPlayerList
        inDB = infoadd.checkPlayerJSON(indPlayer)
        if not inDB:
            playerMiddle = True
            nonSplit = indPlayer.split(" ")
            if len(nonSplit[0]) == 1:
                playerMiddle = False

            if not playerMiddle:
                indPlayer_link = f"https://search.espncricinfo.com/ci/content/site/search.html?search={nonSplit[-1]}"
                html_request = requests.get(indPlayer_link).text
                soup = BeautifulSoup(html_request, 'lxml')
                playerSearch = soup.findAll('h3', class_='name link-cta')
                for pl in playerSearch:
                    playerMatch = noMiddlePattern.match(pl.text)
                    if playerMatch != None and nonSplit[0] in playerMatch.group(2) and nonSplit[-1] in playerMatch.group(1):
                        playerSearch = pl.find('a')
                        playerSearchLink = playerSearch.get('href')
                        playerSearchMatch = playerIDPattern.match(playerSearchLink)
                        playerID = playerSearchMatch.group(2)

                        html_request = requests.get('https://www.espncricinfo.com' + playerSearchLink).text
                        soup = BeautifulSoup(html_request, 'lxml')
                        playerName = soup.find('h1')
                        playerName = playerName.text
                        # playerInfos = soup.findAll('p', class_='ciPlayerinformationtxt')
                        # bowlStyle = "None"
                        # batStyle = "None"
                        # birthMonth = "None"
                        # birthDate = "None"
                        # birthYear = "None"

                        # for info in playerInfos:
                        #     if "Batting style" in info.text:
                        #         batStyle = info.text.replace("Batting style ", "")
                        #         batStyle = batStyle.replace(" bat", "")
                        #     if "Bowling style" in info.text:
                        #         bowlStyle = info.text.replace("Bowling style ", "")
                        #     if "Born" in info.text:
                        #         born = info.text.replace("Born\n\n", "")
                        #         print(born)
                        #         bornMatch = playerBirthPattern.match(born)
                        #         birthMonth = bornMatch.group(1)
                        #         birthDate = bornMatch.group(2)
                        #         birthYear = bornMatch.group(3)


                        country = soup.find("h3", class_="PlayersSearchLink").text
                        country = country.lower()

                        infoadd.addPlayerJSON(playerID, playerName, indPlayer, country)
                        localPlayerList[playerID] = {'initials': indPlayer, 'fullName': playerName}
                    

            else:
                html_request = requests.get(indPlayer_link).text
                soup = BeautifulSoup(html_request, 'lxml')
                playerSearch = soup.find('h3', class_='name link-cta')
                playerSearch = playerSearch.find('a')
                playerSearchLink = playerSearch.get('href')
                playerSearchMatch = playerIDPattern.match(playerSearchLink)
                playerID = playerSearchMatch.group(2)

                html_request = requests.get('https://www.espncricinfo.com' + playerSearchLink).text
                soup = BeautifulSoup(html_request, 'lxml')
                playerName = soup.find('h1')
                playerName = playerName.text
                playerInfos = soup.findAll('p', class_='ciPlayerinformationtxt')
                # bowlStyle = "None"
                # batStyle = "None"
                # birthMonth = "None"
                # birthDate = "None"
                # birthYear = "None"

                # for info in playerInfos:
                #     if "Batting style" in info.text:
                #         batStyle = info.text.replace("Batting style ", "")
                #         batStyle = batStyle.replace(" bat", "")
                #     if "Bowling style" in info.text:
                #         bowlStyle = info.text.replace("Bowling style ", "")
                #     if "Born" in info.text:
                #         born = info.text.replace("Born\n\n", "")
                #         print(born)
                #         bornMatch = playerBirthPattern.match(born)
                #         birthMonth = bornMatch.group(1)
                #         birthDate = bornMatch.group(2)
                #         birthYear = bornMatch.group(3)


                country = soup.find("h3", class_="PlayersSearchLink").text
                country = country.lower()

                infoadd.addPlayerJSON(playerID, playerName, indPlayer, country)
                localPlayerList[playerID] = {'initials': indPlayer, 'fullName': playerName}
        else:
            returnInfo = infoadd.getPlayerID(indPlayer)
            localPlayerList[returnInfo.id] = {'initials': indPlayer, 'fullName': returnInfo.fullName}


    with open(f'data/tests/{matchId}.yaml', "r") as _file: 
        data = yaml.load(_file)
        inningsList = data['innings']
        for inn in inningsList:
            index = inningsList.index(inn)
            inning = None
            if index == 0:
                inning = "1st innings"
            elif index == 1:
                inning = "2nd innings"
            elif index == 2:
                inning = "3rd innings"
            elif index == 3:
                inning = "4th innings"
            
            innings = inn[inning]
            deliveries = innings['deliveries']
            battingTeam = innings['team'].lower()
            for d in deliveries:
                ball = d[next(iter(d))]
                over = next(iter(d))
                non_striker = ball['non_striker']
                non_striker_list = non_striker.split(" ")
                non_striker_link = f"https://search.espncricinfo.com/ci/content/site/search.html?search=+{non_striker_list[0]}%20+{non_striker_list[1]};type=player"
                playerProcessing(non_striker, non_striker_link)

                bowler = ball['bowler']
                bowler_list = bowler.split(" ")
                bowler_link = f"https://search.espncricinfo.com/ci/content/site/search.html?search=+{bowler_list[0]}%20+{bowler_list[1]};type=player"
                playerProcessing(bowler, bowler_link)


                batsman = ball['batsman']
                batsman_list = batsman.split(" ")
                batsman_link = f"https://search.espncricinfo.com/ci/content/site/search.html?search=+{batsman_list[0]}%20+{batsman_list[1]};type=player"
                playerProcessing(batsman, batsman_link)

                extras = ball['runs']['extras']
                batterRuns = ball['runs']['batsman']
                totalRuns = ball['runs']['total']
                
                


                
                