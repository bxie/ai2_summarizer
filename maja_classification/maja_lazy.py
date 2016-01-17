# Maja Svanberg
# maja_lazy.py
# 2016-01-08

from math import sqrt
import json
import unittest
import os
import matplotlib.pyplot as plt


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
        self.assertEqual(blockTypes(self.data)[0], ('hasAboveRange', 0))

    def testBuildTrainer(self):
        self.assertEqual(buildTrainingVectors(combineMany([numScreens]), testDir, 5)[0]\
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
            pass
        elif isinstance(JSON[x][a][b], int):
            result += JSON[x][a][b]
        else:
            result += len(JSON[x][a][b])
    return result

def findNum3(JSON, a, b, c):
    result = 0
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x][a][b] == 'NO ACTIVE BLOCKS':
            pass
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
    return [('numMediaAssets', len(JSON['*Media Assets']))]

def numScreens(JSON):
    return [('numScreens', JSON['*Number of Screens'])]

def numCompAndBlocks(JSON):
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
            result += [('num'+str(feature[0]), findNum3(JSON, feature[1][0], feature[1][1], feature[1][2]))]
        elif len(feature[1]) == 2:
            result += [('num'+str(feature[0]), findNum2(JSON, feature[1][0], feature[1][1]))]
    return result

def componentTypes(JSON):
    compList = ['Camera', 'Canvas', 'Button', 'HorizontalArrangement', 'VerticalArrangement', \
                    'Sound', 'TinyDB', 'LocationSensor', 'Clock', 'PhoneCall', 'Notifier', \
                    'ActivityStarter', 'Label', 'ListPicker', 'PhoneNumberPicker', \
                    'WebViewer', 'Image', 'TextBox', 'TextToSpeech', 'AccelerometerSensor', 'NearField', \
                    'Web', 'Player', 'BluetoothClient', 'BluetoothServer', 'VideoPlayer', 'ImagePicker', \
                    'File', 'ListView', 'DatePicker', 'TimePicker', 'CheckBox', 'Slider', 'PasswordTextBox', \
                    'Spinner', 'TableArrangement', 'YandexTranslate', 'Camcorder', 'SpeechRecognizer', 'SoundRecorder' \
                    'ImageSprite', 'Ball', 'OrientationSensor', 'ProximitySensor', 'EmailPicker', 'Texting', \
                    'Sharing', 'Twitter', 'ContactPicker', 'FusiontablesControl', 'TinyWebDB', \
                    'NxtDrive', 'NxtColorSensor', 'NxtLightSensor', 'NxtSoundSensor', \
                    'NxtTouchSensor', 'NxtUltrasonicSensor', 'NxtDirectCommands']
    result = []
    for comp in compList:
        result += [(str('has'+comp), hasComponent(JSON, comp))] # WEIGH??
    return result

def blockTypes(JSON):
    result = []
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
    blocks = {}
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x]['Blocks']['*Top Level Blocks'] == 'NO ACTIVE BLOCKS':
            pass
        else:
            for key in JSON[x]['Blocks']['*Top Level Blocks']:
                if '.' in key:
                    activity = key.split('.')[1]
                    if activity not in blocks.keys():
                        blocks[activity] = JSON[x]['Blocks']['*Top Level Blocks'][key]
                    else:
                        blocks[activity] += JSON[x]['Blocks']['*Top Level Blocks'][key]
    for block in blockList:
         if block in blocks.keys():
             result += [(str('has' + block), blocks[block])] # WEIGH??
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

def buildTrainingVectors(featurefunc, dirName, numUsers):

    """read summaries from repository, return a list of tuples,
    where each tuple in the list corresponds to a tutorial.
    Each tuple is of the form (status, featurevector),
    where status is if project is a tutorial (here it's always yes),
    and featurevector is the feature vector of the name under featurefunc.
    """
    summaries = findsummaries(dirName, numUsers)
    return map(lambda x: summarytofeature(x, featurefunc), summaries)

def summarytofeature(s, featurefunc):
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

def closestTutorials(projectPath, tutorials, featurefunc, numtut, numClosest):
    '''returns a tuple of (projectpath, (name of closest tutorial, distance))'''
    test = summarytofeature(projectPath, featurefunc)
    training = buildTrainingVectors(featurefunc, tutorials, numtut)
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

def allClosestTutorials(tutorialDir, numtut, projectDir, numPro, featurefunc, numClosest):
    results = []
    projects = findsummaries(projectDir, numPro)
    for project in projects:
        results.append(closestTutorials(project, tutorialDir, featurefunc, numtut, numClosest))
    return results

def filterMatches(bestMatches, bar):
    results = []
    for project in bestMatches:
        goodMatches = []
        for match in project[1]:
            if match[1] <= bar:
                goodMatches.append(match)
        results.append((project[0], goodMatches))
    return results

#print filterMatches([('/Users/Maja/Documents/AI/ai2_users_random/000098/6730814433787904_summary.json', [('HelloPurr', 4.242640687119285), ('geolocation', 6.244997998398398), ('PicCall', 7.0710678118654755), ('TalkToMe', 7.681145747868608), ('PaintPot', 8.0), ('BallBounce', 8.774964387392123), ('Magic8Ball', 14.0)])], 10)

def createPlot(closeTuts):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    X = range(len(closeTuts[1]))
    Y = [x[1] for x in closeTuts[1]]
    print len(X)
    print len(Y)
    plt.plot(X, Y, 'ro')
    plt.axis([-1, len(X), 0, closeTuts[1][-1][1]+1])
    plt.ylabel('Distance to Tutorials')
    plt.title(closeTuts[0])
    for i in X:
        xy = zip(X,[x[1] for x in closeTuts[1]])
        ax.annotate(closeTuts[1][i][0], xy=xy[i])
    plt.show()

def createTrainingFile(dirName, outputName):
    txtf = open(outputName, 'w')
    for source in os.listdir(dirName):
        source = os.path.join(dirName, source)
        if os.path.isdir(source):
            for project in os.listdir(source):
                if project.endswith('summary.json'):
                    txtf.write(source.split('/')[-1] + '/' +  project + '\n')
    txtf.close()    

def main():
    """Runs the classification pipeline with command line arguments"""
    combi = combineMany([blockTypes, componentTypes, numMediaAssets, numScreens, numCompAndBlocks])
   # randomProject = summarytofeature('/Users/Maja/Documents/AI/Tutorials/Wolber/HelloPurr_summary.json', combi)
  #  training =  buildTrainingVectors(combi, '/Users/Maja/Documents/AI/ai2_users_random', 10)
 #   combiDistance = labelsSortedByDistance(randomProject, training)
#    print combiDistance
#    print closestTutorials('/Users/Maja/Documents/AI/Tutorials/Wolber/HelloPurr_summary.json', '/Users/Maja/Documents/AI/ai2_users_random', combi, 100000)
    #findsummaries('/Users/Maja/Documents/AI/Tutorials', 100)
    bm = allClosestTutorials('/Users/Maja/Documents/AI/Tutorials', 100, '/Users/Maja/Documents/AI/ai2_users_random', 104, combi, 10)
    for project in bm:
        for i in range(len(project[1])):
            if project[1][i][1] == 0.0:
                print project[0] + ' is ' + project[1][0][0]
            elif project[1][i][1] <= 2:
                print project[0] + ' might be ' + project[1][i][0]

#    print bm
    #print filterMatches(bm, 10.0)
    createPlot(bm[-1])
#    createTrainingFile('/Users/Maja/Documents/AI/ai2_users_random', 'maja_classification/training.txt')



if __name__=='__main__':  # invoke main() when program is run
    
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testing)
    unittest.TextTestRunner().run(suite)
    main()
