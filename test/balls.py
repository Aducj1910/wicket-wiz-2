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
        playerProfiler.process(file)
