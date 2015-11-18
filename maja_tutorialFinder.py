# Maja Svanberg
# tutorialFinder.py
# 2015-11-04
# for the AI team

import json
import os

def findSimilarities(tutorialSummary, dirName):
    listOfSum = findSummaries(dirName)
    listOfIdentical = []
    listOfSimilar = []
    for proj in listOfSum:
        booleanList = compareProjectToTutorial(proj, tutorialSummary)
        # booleanList has the following shape: [sameName, sameComponents, sameBlocks]
        if booleanList.count(True) == len(booleanList):
            listOfIdentical.append(proj)
        elif True in booleanList:
            listOfSimilar.append(proj)
    return {'Exact matches': listOfIdentical, 'Similar matches': listOfSimilar}

def findSummaries(dirName):
    projects = []
    for user in os.listdir(dirName)[:500]:
        user = os.path.join(dirName, user)
        if os.path.isdir(user):
          for project in os.listdir(user):
              projectPath = os.path.join(user, project)
              if projectPath.endswith('_summary.json'):
                  projects.append(projectPath)
    return projects

def compareProjectToTutorial(projectSum, tutorialSum):
    project = JSONtoDict(projectSum)
    tutorial = JSONtoDict(tutorialSum)
    sameName = compareNames(project[u'**Project Name'], tutorial[u'**Project Name'])
    #sameMedia = compareMedia(project[u'*Media Assets'], tutorial[u'*Media Assets'])
    if project[u'*Number of Screens'] != 0:
        similarScreen1 = compareScreen1(project[u'Screen1'], tutorial[u'Screen1'])
    else:
        similarScreen1 = [False, False]
    return sameName + similarScreen1

def JSONtoDict(JSONfile):
    json_data = open(JSONfile).read()
    return json.loads(json_data)

def compareNames(projectName, tutorialName):
    return [projectName.lower() == tutorialName.lower()]

def compareMedia(projectMedia, tutorialMedia):
    for elt in projectMedia:
        break
    return [len(projectMedia) == len(tutorialMedia)]

def compareScreen1(projectScreen, tutorialScreen):
    similarBlocks = compareBlocks(projectScreen[u'Blocks'], tutorialScreen[u'Blocks'])
    similarComponents = compareComponents(projectScreen[u'Components'], tutorialScreen[u'Components'])
    return similarComponents + similarBlocks

def compareBlocks(projectBlocks, tutorialBlocks):
    if projectBlocks != tutorialBlocks and (projectBlocks != 'NO BLOCKS' or tutorialBlocks != 'NO BLOCKS'):
        return [False]
    elif contains(projectBlocks[u'Active Blocks'][u'Types'].keys(), tutorialBlocks[u'Active Blocks'][u'Types'].keys()):
        numBlockProj = projectBlocks[u'Active Blocks'][u'*Number of Blocks']
        numBlockTut = tutorialBlocks[u'Active Blocks'][u'*Number of Blocks']
        if numBlockProj < numBlockTut + numBlockTut*2 and numBlockProj > numBlockTut + numBlockTut*0.5:
            return [True]
    return [projectBlocks[u'*Top Level Blocks'] == tutorialBlocks[u'*Top Level Blocks'] and projectBlocks[u'Active Blocks'][u'Types'] == tutorialBlocks[u'Active Blocks'][u'Types'] and projectBlocks[u'Orphan Blocks'] == tutorialBlocks[u'Orphan Blocks']]

def contains(small, big):
    for elt in small:
        if elt not in big:
            return False
    return True

def compareComponents(proComps, tutComps):
    if proComps == 'NO COMPONENTS':
        return [False]
    else:
        sameNumComp = proComps[u'Number of Components'] == tutComps[u'Number of Components']
        sameType = proComps[u'Type and Frequency'].keys() == tutComps[u'Type and Frequency'].keys()
        return [sameNumComp and sameType]


# Maja's tests
# print compareProjectToTutorial('/Users/Maja/Documents/AI/Tutorials/Wolber/paintpot2_summary.json', '/Users/Maja/Documents/AI/Tutorials/Wolber/HelloPurr_summary.json')
#print findSummaries('/Users/Maja/Documents/AI/ai2_users_random')
# hey = findSimilarities('/Users/Maja/Documents/AI/Tutorials/Wolber/HelloPurr_summary.json', '/Users/Maja/Documents/AI/ai2_users_random')
# print hey
#for file in hey['Exact matches']:
 #   text = open(file, 'r')
  #  print text.read()
#os.system(hey['Exact matches'])
#print len(hey['Exact matches'])
#print len(hey['Similar matches'])
