from re import match
import yaml,  playerProfiler


def analyse(file, players, matchInfo):
    with open(f'data/tests/{file}.yaml', "r") as _file:
        data = yaml.load(_file)
        info = data['info']
        matchInfo['matchID'] = file
        matchInfo['dates'] = info['dates']
        matchInfo['format'] = info['match_type'] 
        matchInfo['venue'] = info['venue']

        ballByBallDict = playerProfiler.process(file, players)

        for b in ballByBallDict['batter']:
            bInn = ballByBallDict['batter'][b] #ADD ISCAPTAIN & ISWICKETKEEPER
            for p in players:
                if p['id'] in bInn:
                    if b not in p:
                        p[b] = {}
                    p[b]['batting'] = bInn[p['id']]
                else:
                    pass

        for b in ballByBallDict['nonstriker']:
            bInn = ballByBallDict['nonstriker'][b] #ADD ISCAPTAIN & ISWICKETKEEPER
            for p in players:
                if p['id'] in bInn:
                    if b not in p:
                        p[b] = {}
                    p[b]['nonstriker'] = bInn[p['id']]
                else:
                    pass

        for b in ballByBallDict['bowler']:
            bInn = ballByBallDict['bowler'][b] #ADD ISCAPTAIN & ISWICKETKEEPER
            for p in players:
                if p['id'] in bInn:
                    if b not in p:
                        p[b] = {}
                    p[b]['bowling'] = bInn[p['id']]
                else:
                    pass 

        print(players)
