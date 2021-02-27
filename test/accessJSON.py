import json
from re import match

def addMatch(matchInfo):
    with open("matchInfo.json", "r") as jsonFile:
        data = json.load(jsonFile)
    
    id = matchInfo['id']
    data[id] = matchInfo

    with open("matchInfo.json", "w") as jsonFile:
        json.dump(data, jsonFile)

def addIndividual(playersList, matchId):
    with open("individual.json", "r") as jsonFile:
        data = json.load(jsonFile)
    
    for p in playersList:
        if str(p['id']) in data:
            obj = data[p['id']]
            obj[matchId] = p
            data = obj
        else:
            data[p['id']] = {f'{matchId}':p}
    
    with open("individual.json", "w") as jsonFile:
        json.dump(data, jsonFile)

def addMatchup(matchUps, matchId):
    with open("matchups.json", "r") as jsonFile:
        data = json.load(jsonFile)

    
    # for p in matchUps:
    #     if str(p['id']) in data:
    #         obj = data[p['id']]
    #         obj[matchId] = p
    #         data = obj
    #     else:
    #         data[p['id']] = {f'{matchId}':p}
    
    with open("matchups.json", "w") as jsonFile:
        json.dump(data, jsonFile)
            
    
