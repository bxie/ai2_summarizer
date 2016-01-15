# Maja Svanberg
# maja_tutorialFinder2.py
# 2016-01-08
# work in progress

from math import sqrt
import json
import unittest
import os

__author__='Maja'

#Maja's tests
testFile = '/Users/Maja/Documents/AI/ai2_users_random/000000/5335093568602112_summary.json'
testDir = '/Users/Maja/Documents/AI/ai2_users_random'

class testing(unittest.TestCase):

    def testFeatureFunc(self):
        with open(testFile, 'r') as data_file:
            self.data = json.load(data_file)
            data_file.close()
        self.assertEqual(numTopLevelBlocks(self.data), [('numTopLevelBlocks', 2)])
        self.assertEqual(numMediaAssets(self.data), [('numMediaAssets', 0)])
        self.assertEqual(numComponents(self.data), [('numComponents', 5)])
        self.assertEqual(numActiveBlocks(self.data), [('numActiveBlocks', 3)])
        self.assertEqual(numTypesBlocks(self.data), [('numTypesBlocks', 3)])
        self.assertEqual(numTypesComponents(self.data), [('numTypesComponents', 5)])
        self.assertEqual(numStrings(self.data), [('numStrings', 2)])
        self.assertEqual(numScreens(self.data), [('numScreens', 1)])
        self.assertEqual(numGlobVar(self.data), [('numGlobVar', 0)])
        self.assertEqual(numLocVar(self.data), [('numLocVar', 0)])
        self.assertEqual(numProcNames(self.data), [('numProcNames', 0)])
        self.assertEqual(numProcParNames(self.data), [('numProcParNames', 0)])
        self.assertEqual(hasCamera(self.data), [('hasCamera', 0)])
        self.assertEqual(hasCanvas(self.data), [('hasCanvas', 0)])


    def testBuildTrainer(self):
        self.assertEqual(buildTrainingVectors(combineMany([numTopLevelBlocks]), testDir, 5)[0]\
                             , ('texttospeech', [('numTopLevelBlocks', 2)]))

    def testCombine(self):
        lengthFirst = combineMany([numTopLevelBlocks, numMediaAssets, numComponents])

# featureFuncs helpers
# enabling iteration over screens for information located in either 2nd or 
# 3rd level of the dictionary past the screen

def findNum2(JSON, a, b):
    result = 0
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x][a] == 'N' or JSON[x][a] == 'NO ACTIVE COMPONENTS':
            result += 0
        elif isinstance(JSON[x][a][b], int):
            result += JSON[x][a][b]
        else:
            result += len(JSON[x][a][b])
    return result

def findNum3(JSON, a, b, c):
    result = 0
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x][a][b] == 'NO ACTIVE BLOCKS':
            result += 0
        elif isinstance(JSON[x][a][b][c], int):
            result += JSON[x][a][b][c]
        else:
            result += len(JSON[x][a][b][c])
    return result

def hasComponent(JSON, component):
    for x in [key for key in JSON.keys() if key[0] != '*']:
        if JSON[x]['Components'] == 'N':
            pass
        elif component in JSON[x]['Components']['Type and Frequency'].keys():
            return True
    return False

# featureFuncs

def numTopLevelBlocks(JSON):
    return [('numTopLevelBlocks', findNum2(JSON, 'Blocks', '*Top Level Blocks'))]

def numMediaAssets(JSON):
    return [('numMediaAssets', len(JSON['*Media Assets']))]

def numComponents(JSON):
    return [('numComponents', findNum2(JSON, 'Components', 'Number of Components'))]

def numTypesComponents(JSON):
    return [('numTypesComponents', findNum2(JSON, 'Components', 'Type and Frequency'))]

def numActiveBlocks(JSON):
    return [('numActiveBlocks', findNum3(JSON, 'Blocks', 'Active Blocks', '*Number of Blocks'))]

def numTypesBlocks(JSON):
    return [('numTypesBlocks', findNum3(JSON, 'Blocks', 'Active Blocks', 'Types'))]

def numScreens(JSON):
    return [('numScreens', JSON['*Number of Screens'])]

def numStrings(JSON):
    return [('numStrings', findNum3(JSON, 'Blocks', 'Active Blocks', 'Strings') + findNum2(JSON, 'Components', 'Strings'))]

def numGlobVar(JSON):
    return [('numGlobVar', findNum3(JSON, 'Blocks', 'Active Blocks', 'Global Variable Names'))]

def numLocVar(JSON):
    return [('numLocVar', findNum3(JSON, 'Blocks', 'Active Blocks', 'Local Variable Names'))]

def numProcNames(JSON):
    return [('numProcNames', findNum3(JSON, 'Blocks', 'Active Blocks', 'Procedure Names'))]

def numProcParNames(JSON):
    return [('numProcParNames', findNum3(JSON, 'Blocks', 'Active Blocks', 'Procedure Parameter Names'))]

def hasCamera(JSON):
    return [('hasCamera', int(hasComponent(JSON, 'Camera')))]

def hasCanvas(JSON):
    return [('hasCanvas', int(hasComponent(JSON, 'Canvas')))]

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
        return sqrt(sum(map(squareDiff, range(len(v)))))
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

def closestTutorial(projectPath, tutorials, featurefunc, numtut):
    '''returns a tuple of (projectpath, (name of closest tutorial, distance))'''
    test = summarytofeature(projectPath, featurefunc)
    training = buildTrainingVectors(featurefunc, tutorials, numtut)
    return (projectPath, labelsSortedByDistance(test, training)[0])

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

def bestMatches(tutorialDir, numtut, projectDir, numPro, featurefunc):
    results = []
    projects = findsummaries(projectDir, numPro)
    for project in projects:
        results.append(closestTutorial(project, tutorialDir, featurefunc, numtut))
    return results

def filterMatches(bestMatches, bar):
    results = []
    for project in bestMatches:
        if project[1][1] <= 2.0:
            results.append(project)
    return results


def main():
    """Runs the classification pipeline with command line arguments"""
    #combi = combineMany([numActiveBlocks, numComponents, numTopLevelBlocks, numMediaAssets, numStrings, numScreens, numGlobVar, numLocVar, numProcNames, numProcParNames, hasCamera, hasCanvas])
    
#    randomProject = summarytofeature('/Users/Maja/Documents/AI/Tutorials/Wolber/HelloPurr_summary.json', combi)
    #training =  buildTrainingVectors(combi, '/Users/Maja/Documents/AI/Tutorials', 100)
#    combiDistance = labelsSortedByDistance(randomProject, training)
#    combi = combineMany([numActiveBlocks, numComponents, numTopLevelBlocks, numMediaAssets, numStrings, numScreens, numGlobVar, numLocVar, numProcNames, numProcParNames])
    #print closestTutorial('/Users/Maja/Documents/AI/Tutorials/Wolber/HelloPurr_summary.json', '/Users/Maja/Documents/AI/Tutorials', combi, 100)
    #findsummaries('/Users/Maja/Documents/AI/Tutorials', 100)
    #bm = bestMatches('/Users/Maja/Documents/AI/Tutorials', 100, '/Users/Maja/Documents/AI/ai2_users_random', 20, combi)
    #print filterMatches(bm, 2)


if __name__=='__main__':  # invoke main() when program is run
    
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testing)
    unittest.TextTestRunner().run(suite)
    main()

