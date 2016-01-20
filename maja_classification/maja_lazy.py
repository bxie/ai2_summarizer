# Maja Svanberg
# maja_lazy.py
# 2016-01-08

from math import sqrt
import json
import unittest
import os
import matplotlib.pyplot as plt
import numpy as np

__author__='Maja'

#Maja's tests
testFile = '/Users/Maja/Documents/AI/ai2_users_random/000000/5335093568602112_summary.json'
testDir = '/Users/Maja/Documents/AI/ai2_users_random'

class testing(unittest.TestCase):

    def testFeatureFunc(self):
        with open(testFile, 'r') as data_file:
            self.data = json.load(data_file)
            data_file.close()
        self.assertEqual(numMediaAssets(self.data), [('numMediaAssets', 0)])
        self.assertEqual(numScreens(self.data), [('numScreens', 1)])
        self.assertEqual(componentTypes(self.data)[0], ('hasCamera', 0))
        self.assertEqual(numCompAndBlocks(self.data)[0], ('numStrings', 0))
        self.assertEqual(blockTypes(self.data)[1], ('hasAboveRange', 0))
        self.assertEqual(size(self.data), [('size', 7)])

    def testBuildTrainer(self):
        self.assertEqual(buildTrainingVectors(combineMany([numScreens]), testDir)[0]\
                             , ('texttospeech', [('numScreens', 1)]))

    def testCombine(self):
        lengthFirst = combineMany([numMediaAssets, numScreens])


# featureFuncs helpers
# enabling iteration over screens for information located in either 2nd or 
# 3rd level of the dictionary past the screen

def findNum2(JSON, a, b):
    result = 0
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x][a] == 'N' or JSON[x][a] == 'NO ACTIVE COMPONENTS':
            return 0
        elif isinstance(JSON[x][a][b], int):
            result += JSON[x][a][b]
        else:
            result += len(JSON[x][a][b])
    return result

def findNum3(JSON, a, b, c):
    result = 0
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x][a][b] == 'NO ACTIVE BLOCKS':
            return 0
        elif isinstance(JSON[x][a][b][c], int):
            result += JSON[x][a][b][c]
        else:
            result += len(JSON[x][a][b][c])
    return result

def hasComponent(JSON, component):
    result = 0
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x]['Components'] == 'N':
            pass
        elif component in JSON[x]['Components']['Type and Frequency'].keys():
            result += JSON[x]['Components']['Type and Frequency'][component]
    return result

# feature functions 

def numMediaAssets(JSON):
    return [('numMediaAssets', sqrt(float(len(JSON['*Media Assets']))))] # weighed, square root, or log? one media assett instead of 0 means more than 10 instead of 9

def numScreens(JSON):
    return [('numScreens', JSON['*Number of Screens'])]

def numCompAndBlocks(JSON): # weighed, sqrt. 
    result = []
    # featList = [(Feature, (path to feature beyond screen name))]
    featList = [('Strings', ('Blocks', 'Active Blocks', 'Strings')), \
                    ('GlobVar', ('Blocks', 'Active Blocks', 'Global Variable Names')), \
                    ('LocVar', ('Blocks', 'Active Blocks', 'Local Variable Names')), \
                    ('ProcNames',('Blocks', 'Active Blocks', 'Procedure Names')), \
                    ('ProcParNames', ('Blocks', 'Active Blocks', 'Procedure Parameter Names')), \
                    ('TypesBlocks', ('Blocks', 'Active Blocks', 'Types')), \
                    ('ActiveBlocks', ('Blocks', 'Active Blocks', '*Number of Blocks')), \
                    ('TypesComponents', ('Components', 'Type and Frequency')), \
                    ('Components', ('Components', 'Number of Components')), \
                    ('TopLevelBlocks', ('Blocks', '*Top Level Blocks'))]
    for feature in featList:
        if len(feature[1]) == 3:
            result += [('num'+str(feature[0]), sqrt(float(findNum3(JSON, feature[1][0], feature[1][1], feature[1][2]))))]
        elif len(feature[1]) == 2:
            result += [('num'+str(feature[0]), sqrt(float(findNum2(JSON, feature[1][0], feature[1][1]))))] 
    return result

def size(JSON):
    return [('size', #findNum2(JSON, 'Components', 'Number of Components'))] + \
                 findNum3(JSON, 'Blocks', 'Active Blocks', '*Number of Blocks'))]

def componentTypes(JSON): # weighed, *2
    '''takes a json dictionary as an input, and returns a list of featurevectors 
    related to the frequency of each component type'''
    compList = ['Camera', 'Canvas', 'Button', \
                    'Sound', 'TinyDB', 'LocationSensor', 'Clock', 'PhoneCall', 'Notifier', \
                    'ActivityStarter', 'Label', 'ListPicker', 'PhoneNumberPicker', \
                    'WebViewer', 'Image', 'TextBox', 'TextToSpeech', 'AccelerometerSensor', 'NearField', \
                    'Web', 'Player', 'BluetoothClient', 'BluetoothServer', 'VideoPlayer', 'ImagePicker', \
                    'File', 'ListView', 'DatePicker', 'TimePicker', 'CheckBox', 'Slider', 'PasswordTextBox', \
                    'Spinner', 'YandexTranslate', 'Camcorder', 'SpeechRecognizer', 'SoundRecorder' \
                    'ImageSprite', 'Ball', 'OrientationSensor', 'ProximitySensor', 'EmailPicker', 'Texting', \
                    'Sharing', 'Twitter', 'ContactPicker', 'FusiontablesControl', 'TinyWebDB', \
                    'NxtDrive', 'NxtColorSensor', 'NxtLightSensor', 'NxtSoundSensor', \
                    'NxtTouchSensor', 'NxtUltrasonicSensor', 'NxtDirectCommands']
    #'HorizontalArrangement', 'VerticalArrangement', 'TableArrangement' don't affect functionality and can be excluded
    return map(lambda comp: (str('has'+comp), hasComponent(JSON, comp)*2), compList) # weighed

def blockTypes(JSON): # weighed, *2 for top *2 for all. determines functionality.
    '''takes a json dictionary as an input, and returns featvectors related to 
    the frequency of each blocktype in the top level'''
    result = []
    topblocks = {}
    allblocks = {}
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if len(JSON[x]['Blocks']['*Top Level Blocks']) == 0  or \
                JSON[x]['Blocks']['Active Blocks'] == 'NO ACTIVE BLOCKS':
            pass
        else: # can be written more elegantly
            for key in JSON[x]['Blocks']['*Top Level Blocks']:
                if '.' in key:
                    activity = key.split('.')[1]
                    if activity not in topblocks.keys():
                        topblocks[activity] = JSON[x]['Blocks']['*Top Level Blocks'][key]
                    else:
                        topblocks[activity] += JSON[x]['Blocks']['*Top Level Blocks'][key]
            for key in JSON[x]['Blocks']['Active Blocks']['Types']:
                if '.' in key:
                    activity = key.split('.')[1]
                    if activity not in allblocks.keys():
                        allblocks[activity] = JSON[x]['Blocks']['Active Blocks']['Types'][key]
                    else:
                        allblocks[activity] += JSON[x]['Blocks']['Active Blocks']['Types'][key]
    for block in blockList:
         if block in topblocks.keys():
             result += [(str('hasTop' + block), topblocks[block]*4)] # WEIGHED
         else:
             result += [(str('hasTop' + block), 0)]
         if block in allblocks.keys():
             result += [(str('has' + block), allblocks[block]*2)] # WEIGHED
         else:
             result += [(str('has' + block), 0)]
    return result

# combining function

def combineMany(listOfFeatureFuncs):
    """returns a function that, when applied to a name, returns a feature vector
    combining the feature vectors from featureFunc1 and featureFunc2"""
    return reduce(lambda x, y: (lambda z: x(z) + y(z)), listOfFeatureFuncs)

# euclidian distance function (adapted from CS111/F15/PSET11)

def euclideanDistanceFrom(v):
    """returns a function that takes a vector and computes the distance between that vector and v"""
    def euclideanDistanceHelper(w):
        """distance between vectors v and w"""
        def squareDiff(i):
            """square of difference between elements in ith position of vectors v and w"""
            return (v[1][i][1] - w[i][1])**2
        return sqrt(sum(map(squareDiff, range(len(v[1])))))
    return euclideanDistanceHelper

def buildTrainingVectors(featurefunc, dirName):
    """read summaries from repository, return a list of tuples,
    where each tuple in the list corresponds to a tutorial.
    Each tuple is of the form (status, featurevector),
    where status is if project is a tutorial (here it's always yes),
    and featurevector is the feature vector of the name under featurefunc.
    """
    summaries = findsummaries(dirName, 100)
    return map(lambda x: summarytofeature(x, featurefunc), summaries)

def summarytofeature(s, featurefunc):
    '''takes a JSON summary and translates it into a dict, 
    and returns a tuple (path, features) for the summary'''
    with open(s, 'r') as data_file:
            JSON = json.load(data_file)
            data_file.close()
            return (str(JSON['**Project Name']), featurefunc(JSON))

def labelsSortedByDistance(testvector, trainingVectors):
    """creates a list of (tutorialName, distance) tuples from trainingVectors
    (trainingVectors is a list of (tutorialNames, featvec) tuples, 
    of the type returned by buildTrainingVectors).
    The distance is the Euclidean distance between featvec and testvector.
    Sorts this list of tuples by distance"""
    euclideanDistance = euclideanDistanceFrom(testvector)
    return sorted(map(lambda x: (x[0], euclideanDistance(x[1])), trainingVectors), key=lambda name:name[1])

def closestTutorials(projectPath, tutorials, featurefunc, numClosest):
    '''returns a tuple of (projectpath, (name of closest tutorial, distance))'''
    test = summarytofeature(projectPath, featurefunc)
    training = buildTrainingVectors(featurefunc, tutorials)
    return (projectPath, labelsSortedByDistance(test, training)[:numClosest])

def findsummaries(dirName, numUsers):
    '''returns a list of JSON summaries from a directory'''
    summaries = []
    for source in os.listdir(dirName)[:numUsers]:
        source = os.path.join(dirName, source)
        if os.path.isdir(source):
            for project in os.listdir(source):
                if project.endswith('summary.json'):
                    summaries.append(os.path.join(source, project))
    return summaries


def allClosestTutorials(tutorialDir, projectDir, numPro, featurefunc, numClosest):
    '''returns the numClosest closest tutorials from numPro projects in projectDir'''
    return map(lambda x: closestTutorials(x, tutorialDir, featurefunc, numClosest), \
                   findsummaries(projectDir, numPro))


def instanceClosestTutorials(trainFile, proDir, tutorialDir, featurefunc, numClosest):
    '''returns the closest tutorials for each identified project from TrainFile'''
    tutorials = listsOfInstances(trainFile)[0]
    nottutorials = listsOfInstances(trainFile)[1]
    return map(lambda x: closestTutorials(x, tutorialDir, featurefunc, numClosest), \
                   map(lambda x: proDir + '/' + x, tutorials)), \
                   map(lambda x: closestTutorials(x, tutorialDir, featurefunc, numClosest), \
                           map(lambda x: proDir + '/' + x, nottutorials))

def sizeOfInstances(trainFile, proDir):
    tutorials = listsOfInstances(trainFile)[0]
    nottutorials = listsOfInstances(trainFile)[1]
    return map(lambda x: summarytofeature(x, size), \
                   map(lambda x:proDir + '/' + x, tutorials)), \
                   map(lambda x: summarytofeature(x, size), \
                           map(lambda x: proDir + '/' + x, nottutorials))

# helpfunction for instanceClosestTutorials
def listsOfInstances(trainFile):
    projects = open(trainFile, 'r').readlines()
    tutorials = []
    notTutorials = []
    for project in projects:
        project = project.split()
        if project[1] == str(True):
            tutorials.append(project[0])
        else:
            notTutorials.append(project[0])
    return tutorials, notTutorials


def dumpToJSON(projects, outputfile):
    with open (outputfile, 'w')as outFile:
        outFile.write(json.dumps(projects,
                             sort_keys=True,
                             indent=2, separators=(',', ':')))


def main():
    #Maja's tests
    #combi = combineMany([blockTypes, numMediaAssets, numScreens, componentTypes, numCompAndBlocks])
    #bm = instanceClosestTutorials('maja_classification/training.txt', '/Users/Maja/Documents/AI/ai2_users_random', '/Users/Maja/Documents/AI/Tutorials', combi, 1)
    #dumpToJSON(bm, 'instanceClosestTutorials.json')
    pass

blockList = ['AboveRange', 'ActivityCanceled', 'AccelerationChanged', 'AfterActivity', \
                     'AfterChoosing', 'AfterFileSaved', 'AfterGettingText', 'AfterPicking', \
                     'AfterPicture', 'AfterRecording', 'AfterSelecting', 'AfterSoundRecorded', \
                     'AfterScan', 'AfterSpeaking', 'AfterTextInput', 'AfterTimeSet', \
                     'BeforeGettingText', 'BeforeSpeaking', 'BelowRange', 'Changed', 'Click',\
                     'CollidedWith', 'ColorChanged', 'Completed', 'ConnectionAccepted', \
                     'DirectMessagesReceived', 'Dragged', 'FollowersReceived', 'FriendTimelineReceived', \
                     'GotFile', 'GotFocus', 'GotResult', 'GotText', 'GotTranslation', 'GotValue', \
                     'IsAuthorized', 'LocationChanged', 'IncomingCallAnswered', 'LongClick', \
                     'LostFocus', 'AccelerationChanged', 'Shaking', 'MentionsReceived', \
                     'MessageReceived', 'Timer', 'Initialize', 'OrientationChanged', 'OtherPlayerStarted',\
                     'PhoneCallEnded', 'PhoneCallStarted',  'NoLongerCollidingWith', 'PositionChanged', \
                     'ProximityChanged', 'SearchSuccessful', 'StartedRecording', 'StatusChanged', \
                     'StoppedRecording','TagRead', 'TagWritten',  'Touched', 'TouchDown', 'TouchUp', \
                     'ValueStored', 'WebServiceError', 'WithinRange', 'EdgeReached', 'Flung',\
                     'Pressed', 'Released']


if __name__=='__main__':  
    
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testing)
    unittest.TextTestRunner().run(suite)
    main()
