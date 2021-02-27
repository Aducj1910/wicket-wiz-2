import yaml
from bs4 import BeautifulSoup
import requests
import re
import infoadd

playerIDPattern = re.compile(r"(\/.+?(?=\/)){3}\/(.+?(?=\.html))") #group2 - playerID
playerBirthPattern = re.compile(r"(.+?(?=\s))(.+?(?=,)),\s(.+?(?=,))") #group1 - month, #group2 - date, #group3 - year
noMiddlePattern = re.compile(r"(.+?(?=,)),\s(.+)") #group1 - first, #group2 - last

localPlayerList = {}

masterBowlers = {}
masterBatters = {}
masterNonstrikers = {}

def process(matchId, checkAgainstPlayersList):
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
                        match = False
                        playerSearch = pl.find('a')
                        playerSearchLink = playerSearch.get('href')
                        playerSearchMatch = playerIDPattern.match(playerSearchLink)
                        playerID = playerSearchMatch.group(2)

                        for kk in checkAgainstPlayersList:
                            if kk['id'] == playerID:
                                match = True

                        if match == True:
                            html_request = requests.get('https://www.espncricinfo.com' + playerSearchLink).text
                            soup = BeautifulSoup(html_request, 'lxml')
                            playerName = soup.find('h1')
                            playerName = playerName.text
                            country = soup.find("h3", class_="PlayersSearchLink").text
                            country = country.lower()
                            infoadd.addPlayerJSON(playerID, playerName, indPlayer, country)
                            localPlayerList[indPlayer] = {'id': playerID, 'fullName': playerName}             
                            break                
                

            else:
                html_request = requests.get(indPlayer_link).text
                soup = BeautifulSoup(html_request, 'lxml')
                playerSearchInit = soup.findAll('h3', class_='name link-cta')

                index_ = 0
                while True:
                    playerSearch = playerSearchInit[index_]
                    playerSearch = playerSearch.find('a')
                    playerSearchLink = playerSearch.get('href')
                    playerSearchMatch = playerIDPattern.match(playerSearchLink)
                    playerID = playerSearchMatch.group(2)
                    match = False
                    for kk in checkAgainstPlayersList:
                        if playerID == kk['id']:
                            match = True
                    if match:
                        break
                    else:
                        index_ += 1

                

                html_request = requests.get('https://www.espncricinfo.com' + playerSearchLink).text
                soup = BeautifulSoup(html_request, 'lxml')
                playerName = soup.find('h1')
                playerName = playerName.text
                playerInfos = soup.findAll('p', class_='ciPlayerinformationtxt')

                country = soup.find("h3", class_="PlayersSearchLink").text
                country = country.lower()

                infoadd.addPlayerJSON(playerID, playerName, indPlayer, country)
                localPlayerList[indPlayer] = {'id': playerID, 'fullName': playerName}
        else:
            returnInfo = infoadd.getPlayerID(indPlayer)
            localPlayerList[indPlayer] = {'id': returnInfo['id'], 'fullName': returnInfo['fullName']}


    with open(f'data/tests/{matchId}.yaml', "r") as _file: 
        data = yaml.load(_file)
        teamList = data['info']['teams']
        inningsList = data['innings']
        numberInn = len(inningsList)
        for inn in inningsList:      

            trackerListBatter = {}
            trackerListNonstriker = {}
            trackerListBowler = {}
            trackerMatchups = {}

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
                bowlerR = bowler
                bowler_list = bowler.split(" ")
                bowler_link = f"https://search.espncricinfo.com/ci/content/site/search.html?search=+{bowler_list[0]}%20+{bowler_list[1]};type=player"
                playerProcessing(bowler, bowler_link)


                batsman = ball['batsman']
                batsman_list = batsman.split(" ")
                batsman_link = f"https://search.espncricinfo.com/ci/content/site/search.html?search=+{batsman_list[0]}%20+{batsman_list[1]};type=player"
                playerProcessing(batsman, batsman_link)

                batsman = localPlayerList[batsman]['id']
                bowler = localPlayerList[bowler]['id']
                non_striker = localPlayerList[non_striker]['id']

                extras = ball['runs']['extras']
                batterRuns = ball['runs']['batsman']
                totalRuns = ball['runs']['total']
                runsConceded = totalRuns

                extraKind = None
                howOut = None
                nonStrikerOut = False
                wicket = False
                balls = 1
                wickets = 0

                catcher = None
                stumper = None

                if extras != 0:
                    extraKind = next(iter(ball['extras']))
                    if extraKind == 'noballs':
                        balls = 0
                    if extraKind == 'wides':
                        balls = 0
                    if extraKind == 'byes' or extraKind == 'legbyes':
                        runsConceded = runsConceded - extras

                if 'wicket' in ball:
                    howOut = ball['wicket']['kind']
                    if ball['wicket']['player_out'] == non_striker:
                        nonStrikerOut = True
                    if howOut != 'run out':
                        wickets = 1
                    if howOut == 'caught':
                        catcher = ball['wicket']['fielders'][0]
                        catcher = infoadd.getPlayerID(catcher)['id']
                    if howOut == 'stumped':
                        stumper = ball['wicket']['fielders'][0]
                        stumper = infoadd.getPlayerID(stumper)['id']
                    if howOut == 'caught and bowled':
                        catcher = bowler
                        

                    wicket = True
                
                ballObj = {str(over): {'runs': totalRuns, 'extras': extras, 'batterRuns': batterRuns, 'howOut': howOut, 'wicket': wicket, 'extrasKind': extraKind, 'nonStriker': non_striker, 'batter': batsman, 'bowler': bowler, 'catcher': catcher, 'stumper': stumper}}

                if non_striker not in trackerListNonstriker:
                    trackerListNonstriker[non_striker] = {'runs': batterRuns, 'balls': balls, 'extras': extras, 'ballsList': [ballObj]}
                else: 
                    obj = trackerListNonstriker[non_striker]
                    obj['runs'] += totalRuns
                    obj['balls'] += balls
                    obj['extras'] += extras
                    obj['ballsList'].append(ballObj)
                    trackerListNonstriker[non_striker] = obj

                if batsman not in trackerListBatter:
                    trackerListBatter[batsman] = {'runs': batterRuns, 'balls': balls, 'extras': extras, 'ballsList': [ballObj]}
                else:
                    obj = trackerListBatter[batsman]
                    obj['runs'] += totalRuns
                    obj['balls'] += balls
                    obj['extras'] += extras
                    obj['ballsList'].append(ballObj)
                    trackerListBatter[batsman] = obj

                if bowler not in trackerListBowler:
                    trackerListBowler[bowler] = {'runsConceded': runsConceded, 'balls': balls, 'extras': extras, 'wickets': wickets, 'ballsList': [ballObj]}
                else:
                    obj = trackerListBowler[bowler]
                    obj['runsConceded'] += runsConceded
                    obj['balls'] += balls
                    obj['extras'] += extras
                    obj['ballsList'].append(ballObj)
                    obj['wickets'] += wickets
                    trackerListBowler[bowler] = obj    

            masterBatters[inning] = trackerListBatter             
            masterBowlers[inning] = trackerListBowler
            masterNonstrikers[inning] = trackerListNonstriker
    
    # print(masterBowlers)
    return {'batter': masterBatters, 'bowler': masterBowlers, 'nonstriker': masterNonstrikers, 'inningsNumber': numberInn}


                

                
                

                


                
                


                
                