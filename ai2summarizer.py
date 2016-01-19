# Maja Svanberg
# AI2 summarizer
# Code adapted from jail.py

# Version as of 2015/11/11 with edits by lyn to replace
# component_event, component_method, component_set_get
# by component-specific details. E.g.
# * not component_event, but Canvas.Draggged, ListPicker.AfterPicking, etc.
# * not component_method, but Canvas.DrawLine
# * not component_set_get, but Label.GetText, Label.SetText


import os
import os.path
import json
import zipfile
import xml.etree.ElementTree as ET
import re

def allProjectsToJSONFiles(userDir, numUsers):
    '''assumes cwd contains dir, that contains projects (in .aia, .zip, or as dir)'''
    listOfAllProjects = findProjectDirs(userDir, numUsers)
    for project in listOfAllProjects:
        if os.path.exists(project):
            projectToJSONFile(project)
            if os.path.exists(project.split('.')[0]) and project.split('.')[1] == 'zip':
                os.remove(project)


def findProjectDirs(dirName, numUsers):
    projects = []
    for user in os.listdir(dirName)[:numUsers]:
        user = os.path.join(dirName, user)
        if os.path.isdir(user):
          for project in os.listdir(user):
              projectPath = os.path.join(user, project)
              if os.path.isdir(projectPath):
                  projects.append(zipdir(projectPath, projectPath + '.zip'))
              elif projectPath.endswith('.aia') or projectPath.endswith('.zip'):
                  projects.append(projectPath)
    return projects

def zipdir(path, ziph):
    zf = zipfile.ZipFile(ziph, "w")
    for root, dirs, files in os.walk(path):
        for file in files:
            zf.write(os.path.join(root, file))
    zf.close()
    return ziph

def projectToJSONFile(projectPath):
    jsonProjectFileName = projectPath.split('.')[0] + '_summary.json'
    jsonProject = projectToJSON(projectPath)
    with open (jsonProjectFileName, 'w') as outFile:
        outFile.write(json.dumps(jsonProject,
                             sort_keys=True,
                             indent=2, separators=(',', ':')))

def projectToJSON(projectPath):
    summary = {}
    if not projectPath.endswith('zip') and not projectPath.endswith('.aia'):
        raise Exception("project is not .aia or  .zip")
    with zipfile.ZipFile(projectPath, 'r') as myZip:
        summary['**Project Name'] = findName(myZip)
        listOfScreens = findScreenNames(myZip)
        summary['*Number of Screens'] = len(listOfScreens)
        media = []
        for screen in listOfScreens:
            screenInfo = screenToJSON(myZip, screen, projectPath)
            summary[str(screen)] = screenInfo[0]
            media += screenInfo[1]
        summary['*Media Assets'] = list(set(media))
    return summary


'''Given a Python zip file and a pathless filename (no slashes), extract the lines from filename,             
   regardless of path. E.g., Screen1.bky should work if archive name is Screen1.bky                                                                                  or src/appinventor/ai_fturbak/PROMOTO_IncreaseButton/Screen1.bky. 
   it also strips the file from '&'s and '>'  '''
def linesFromZippedFile(zippedFile, pathlessFilename):
    if "/" in pathlessFilename:
        raise RuntimeError("linesFromZippedFile -- filename should not contain slash: " + pathlessFilename)
    names = zippedFile.namelist()
    if pathlessFilename in names:
        fullFilename = pathlessFilename
    else:
        matches = filter(lambda name: name.endswith("/" + pathlessFilename), names)
        if len(matches) == 1:
            fullFilename = matches[0]
        elif len(matches) == 0:
            raise RuntimeError("linesFromZippedFile -- no match for file named: " + pathlessFilename)
        else:
            raise RuntimeError("linesFromZippedFile -- multiple matches for file named: "
                         + pathlessFilename
                         + "[" + ",".join(matches) + "]")
    return zippedFile.open(fullFilename).readlines()

def findName(zippedFile): 
    pp = linesFromZippedFile(zippedFile, 'project.properties') 
    return  pp[1][:-1].split('=')[1]

def findScreenNames(zippedFile): 
    names = zippedFile.namelist()
    screens = []
    for file in names:
        if str(file)[-4:] == '.bky':
            screens.append(str(file.split('/')[-1])[:-4])
    return screens

def screenToJSON(zippedFile, screenName, projectPath):
    components = scmToComponents(zippedFile, screenName + '.scm')
    bky = bkyToSummary(zippedFile, screenName + '.bky', projectPath)
    return {'Components': components[0], 'Blocks': bky}, components[1] 

def scmToComponents(zippedFile, scmFileName):
    scmLines = linesFromZippedFile(zippedFile, scmFileName)
    if (len(scmLines) == 4
        and scmLines[0].strip() == '#|'
        and scmLines[1].strip() == '$JSON'
        and scmLines[3].strip() == '|#'):
        data = json.loads(scmLines[2])
    else:
        data = json.loads(scmLines)
    strings = []
    components = {}
    media = []
    if u'$Components' not in data[u'Properties'].keys():
        return 'NO COMPONENTS'
    else:
        for component in data[u'Properties'][u'$Components']:
            if component[u'$Type'] in components:
                components[component['$Type']] += 1
            else: 
                components[component['$Type']] = 1
            if u'Text' in component.keys():
                strings.append(component[u'Text'])
            media += findMedia(component)
    return {'Number of Components': len(components), 'Type and Frequency': components, 'Strings': strings}, media

def findMedia(component):
    media = []
    for elt in component.values():
        if isinstance(elt, basestring) and len(elt.split('.')) == 2:
            ext = elt.split('.')[1]
            for key in component.keys():
                if component[key] == elt and elt not in media and (key == 'Picture' or \
                                                                       key == 'Image' or \
                                                                       key == 'Source' or \
                                                                       key == 'BackgroundImage' or \
                                                                       key == 'ResponseFileName'): # theses were the only keys I found in any of the tutorials that had files as values. // Maja 2015/12/27
                    media.append(elt)
        elif isinstance(elt, list):
            for comp in elt:
                media += findMedia(comp)
    return media

def elementTreeFromLines(lines, projectPath):
    """ This function is designed to handle the following bad case: <xml xmlns="http://www.w3.org/1999/xhtml">
    for each file parse the xml to have a tree to run the stats collection on
    assumes if a namespace exists that it's only affecting the xml tag which is assumed to be the first tag"""
    # lines = open(filename, "r").readlines()                                     
    try:
        firstline = lines[0] #we are assuming that firstline looks like: <xml...>... we would like it to be: <xml>...                                                             
        if firstline[0:4] != "<xml":
            return ET.fromstringlist(['<xml></xml>'])
        else:
            closeindex = firstline.find(">")
            firstline = "<xml>" + firstline[closeindex + 1:]
            lines[0] = firstline
     #Invariant: lines[0] == "<xml>..." there should be no need to deal with namespace issues now
            return ET.fromstringlist(lines)
    except (IndexError, ET.ParseError):
        print (str(projectPath) + " bky malformed")
        return ET.fromstringlist(['<MALFORMED></MALFORMED>'])

def bkyToSummary(zippedFile, bkyFileName, projectPath):
  bkyLines = linesFromZippedFile(zippedFile, bkyFileName)
  rootElt = elementTreeFromLines(bkyLines, projectPath)
  if rootElt.tag == 'MALFORMED':
      return 'MALFORMED BKYFILE'
  elif not rootElt.tag == 'xml':
      raise RuntimeError('bkyToSummary: Root of bky file is not xml but ' + rootElt.tag)
  else:
      listOfBlocks = []
      listOfOrphans = []
      top  = []
      if len(rootElt) < 1:
          return 'NO BLOCKS'
      for child in rootElt:
          if child.tag == 'block':
              type = child.attrib['type']
              top.append(blockType(child, zippedFile, bkyFileName)) # [lyn, 2015/11/11] Specially handle component_event, component_method, component_set_get
              component_selector = False
              for grandchild in child:
                  if grandchild.tag == 'title' or grandchild.tag =='field':
                      if grandchild.attrib['name'] == 'COMPONENT_SELECTOR':
                          component_selector = True
              if type in ['component_event', 'global_declaration', 'procedures_defnoreturn', \
                              'procedures_defreturn', 'procedures_callnoreturn', 'procedures_callreturn'] \
                              or type[:-4] == 'lexical_variable':
                  listOfBlocks += findBlockInfo(child, zippedFile, bkyFileName)
              else:
                  listOfOrphans += findBlockInfo(child, zippedFile, bkyFileName)
      if len(listOfBlocks) == 0:
          blocks = 'NO ACTIVE BLOCKS'
      else:
          blocks = formatLists(listOfBlocks)
      if len(listOfOrphans) == 0:
          orphans = 'NO ORPHAN BLOCKS'
      else:
          orphans = formatLists(listOfOrphans)
      return {'*Top Level Blocks': sortToDict(top), 'Active Blocks': blocks, 'Orphan Blocks': orphans}

def formatLists(inputList):
      blockDict = {}
      blockDict['Types'] = []
      blockDict['*Number of Blocks'] = len(inputList)
      blockDict['Procedure Names'] = []
      blockDict['Procedure Parameter Names'] = []
      blockDict['Global Variable Names'] = []
      blockDict['Local Variable Names'] = []
      blockDict['Strings'] = []
      for dict in inputList:
          for key in dict:
              if key == 'Type':
                  blockDict['Types'].append(dict[key])
              else:
                  blockDict[key] += dict[key]
      for key in blockDict:
          if key != '*Number of Blocks':
              blockDict[key] = sortToDict(blockDict[key])
      return blockDict

def sortToDict(list):
    output = {}
    for elt in list:
        if elt not in output.keys():
            output[elt] = 1
        else:
            output[elt] += 1
    return output

def findBlockInfo(xmlBlock, zippedFile, bkyFileName):
    blockDict = {}
    type = blockType(xmlBlock, zippedFile, bkyFileName) # [lyn, 2015/11/11] Specially handle component_event, component_method, component_set_get [Maja, 2015/11/15] passing down zippedFile and bkyFileName to be able to handle old formatting
    blockDict['Type'] = type
    blockDict['Procedure Names'] = []
    blockDict['Procedure Parameter Names'] = []
    blockDict['Global Variable Names'] = []
    blockDict['Local Variable Names'] = []
    blockDict['Strings'] = []
    subBlocks = []
    if type  == 'procedures_defnoreturn' or type == 'procedures_defreturn' or type == 'procedures_callnoreturn' or type == 'procedures_callreturn':
        for child in xmlBlock:
            if child.tag == 'title' or child.tag == 'field':
                blockDict['Procedure Names'] = [child.text]
            for param in child:
                if param.tag == 'arg':
                    blockDict['Procedure Parameter Names'].append(param.attrib['name'])
    if type  == 'global_declaration' or type == 'lexical_variable_get' or  type == 'lexical_variable_set':
        for child in xmlBlock:
            if child.tag == 'field' or child.tag == 'title':
                blockDict['Global Variable Names'].append(child.text)
    if type == 'local_declaration_statement' or type == 'local_declaration_expression':
        for child in xmlBlock:
            if child.tag == 'title' or child.tag == 'field':
                blockDict['Local Variable Names'].append(child.text)
    if type == 'text':
        for child in xmlBlock:
            if child.tag == 'title' or child.tag == 'field':
                blockDict['Strings'].append(child.text)
    subBlocks = []
    for child in xmlBlock:
        for grandchild in child:
            if grandchild.tag == 'block':
                subBlocks += findBlockInfo(grandchild, zippedFile, bkyFileName)
    return [blockDict] + subBlocks

def blockType(xmlBlock, zippedFile, bkyFileName):
    type = xmlBlock.attrib['type']
    if type == 'component_event':
        for child in xmlBlock:
            if child.tag == 'mutation':
                return child.attrib['component_type'] + "." + child.attrib['event_name']
    elif type == 'component_method':
        for child in xmlBlock:
            if child.tag == 'mutation':
                return child.attrib['component_type'] + "." + child.attrib['method_name']
    elif type == 'component_set_get':
        for child in xmlBlock:
            if child.tag == 'mutation':
                return child.attrib['component_type'] + "." \
                       + child.attrib['set_or_get'].capitalize() + child.attrib['property_name']
    elif type not in blockTypeDict.keys():
        return upgradeFormat(type, zippedFile, bkyFileName) # [Maja, 2015/11/15] handles the old style formatting e.g. 'DrawingCanvas_Clicked' --> 'Canvas.Clicked'
    else:
        return type

# [Maja, 2015/11/15]
def upgradeFormat(type, zippedFile, bkyFileName):
    action = type.split('_')[-1]
    compType = findComponentType(type.split('_')[:-1], zippedFile, bkyFileName[:-4] + '.scm')
    return str(compType) + '.' + str(action)

def findComponentType(compName, zippedFile, scmfile):
    ''' takes the component name, opens the .scm file, and finds the type of component '''
    scmLines = linesFromZippedFile(zippedFile, scmfile)
    if (len(scmLines) == 4
        and scmLines[0].strip() == '#|'
        and scmLines[1].strip() == '$JSON'
        and scmLines[3].strip() == '|#'):
        data = json.loads(scmLines[2])
    for comp in data[u'Properties'][u'$Components']:
        if comp[u'$Type'][-11:] == 'Arrangement':
            for elt in comp[u'$Components']:
                if str(elt[u'$Name']) == compName[0]:
                    return elt[u'$Type']
        elif str(comp[u'$Name']) == compName[0]:
            return comp[u'$Type']

"""
Given the path to a directory that contains users (dirName) and a file extension (fileType),
remove all files in the project directory that end with that file extension
"""
def cleanup(dirName, fileType):
    for user in os.listdir(dirName):
        user = os.path.join(dirName, user)
        if os.path.isdir(user):
          for project in os.listdir(user):
              projectPath = os.path.join(user, project)
              if projectPath.endswith(fileType):
                  os.remove(projectPath)

''' from jail.py '''
blockTypeDict = {

  # Component events                                                                                                    
  'component_event': {'kind': 'declaration'},

  # Component properties                                                                                                
  # These are handled specially in determineKind, which does not check these entries for kind                           
  'component_get': {'argNames': [], 'kind': 'expression'},
  'component_set': {'argNames': ['VALUE'], 'kind': 'statement'},

  # Component method calls                                                                                              
  # These are handled specially in determineKind, which does not check these entries for kind                           
  'component_method_call_expression': {'kind': 'expression'},
  'component_method_call_statement': {'kind': 'statement'},

  # Component value blocks (for generics)                                                                               
  'component_component_block': {'argNames': [], 'kind': 'expression'},

  # Variables                                                                                                          \
                                                                                                                        
  'global_declaration': {'argNames': ['VALUE'], 'kind': 'declaration'},
  'lexical_variable_get': {'argNames': [], 'kind': 'expression'},
  'lexical_variable_set': {'argNames': ['VALUE'], 'kind': 'statement'},
  'local_declaration_statement': {'kind': 'statement'},
  'local_declaration_expression': {'kind': 'expression'},
 # Procedure declarations and calls                                                                                   \
                                                                                                                        
  'procedures_defnoreturn': {'kind': 'declaration'},
  'procedures_defreturn': {'kind': 'declaration'},
  'procedures_callnoreturn': {'kind': 'statement'},
  'procedures_callreturn': {'kind': 'expression'},

  # Control blocks
                                                                                                                        
  'controls_choose': {'argNames': ['TEST', 'THENRETURN', 'ELSERETURN'], 'kind': 'expression'},
  'controls_if': {'kind': 'statement'}, # all sockets handled specially                                                 
  'controls_eval_but_ignore': {'argNames':['VALUE'], 'kind': 'statement'},
  'controls_forEach': {'argNames': ['LIST'], 'kind': 'statement'}, # body statement socket handled specially            
  'controls_forRange': {'argNames': ['START', 'END', 'STEP'], 'kind': 'statement'}, # body statement socket handled specially
  'controls_while': {'argNames': ['TEST'], 'kind': 'statement'}, # body statement socket handled specially              
  'controls_do_then_return': {'kind': 'expression'}, # all sockets handled specially                                    

  # Control ops on screen:                                                                                                             
  'controls_closeApplication': {'argNames':[], 'kind': 'statement'},
  'controls_closeScreen': {'argNames':[], 'kind': 'statement'},
  'controls_closeScreenWithPlainText': {'argNames':['TEXT'], 'kind': 'statement'},
  'controls_closeScreenWithValue': {'argNames':['SCREEN'], 'kind': 'statement'},
  'controls_getPlainStartText': {'argNames':[], 'kind': 'expression'},
  'controls_getStartValue': {'argNames':[], 'kind': 'expression'},
  'controls_openAnotherScreen': {'argNames':['SCREEN'], 'kind': 'statement'},
  'controls_openAnotherScreenWithStartValue': {'argNames':['SCREENNAME', 'STARTVALUE'], 'kind': 'statement'},

  # Colors

  'color_black': {'argNames': [], 'kind': 'expression'},
  'color_blue': {'argNames': [], 'kind': 'expression'},
  'color_cyan': {'argNames': [], 'kind': 'expression'},
  'color_dark_gray': {'argNames': [], 'kind': 'expression'},
  'color_light_gray': {'argNames': [], 'kind': 'expression'},
  'color_gray': {'argNames': [], 'kind': 'expression'},
  'color_green': {'argNames': [], 'kind': 'expression'},
  'color_magenta': {'argNames': [], 'kind': 'expression'},
  'color_orange': {'argNames': [], 'kind': 'expression'},
  'color_pink': {'argNames': [], 'kind': 'expression'},
  'color_red': {'argNames': [], 'kind': 'expression'},
  'color_white': {'argNames': [], 'kind': 'expression'},
  'color_yellow': {'argNames': [], 'kind': 'expression'},

  # Color ops:                                                                                                         \
                                                                                                                        
  'color_make_color': {'argNames':['COLORLIST'], 'kind': 'expression'},
  'color_split_color': {'argNames':['COLOR'], 'kind': 'expression'},

  # Logic                                                                                                               
  'logic_boolean': {'argNames': [], 'kind': 'expression'},
  'logic_false': {'argNames': [], 'kind': 'expression'}, # Together with logic boolean                                  
  'logic_compare': {'argNames': ['A', 'B'], 'kind': 'expression'},
  'logic_negate': {'argNames': ['BOOL'], 'kind': 'expression'},
  'logic_operation': {'argNames': ['A', 'B'], 'kind': 'expression'},
  'logic_or': {'argNames': ['A', 'B'], 'kind': 'expression'}, # Together with logic_operation                           

  # Lists                                                                                                               
  'lists_create_with': {'expandableArgName': 'ADD', 'kind': 'expression'},
  'lists_add_items': {'argNames': ['LIST'], 'expandableArgName':'ITEM', 'kind': 'statement'},
  'lists_append_list': {'argNames': ['LIST0', 'LIST1'], 'kind': 'statement'},
  'lists_copy': {'argNames': ['LIST'], 'kind': 'expression'},
  'lists_insert_item': {'argNames': ['LIST', 'INDEX', 'ITEM'], 'kind': 'statement'},
  'lists_is_list': {'argNames': ['ITEM'], 'kind': 'expression'},
  'lists_is_in': {'argNames':['ITEM', 'LIST'], 'kind': 'expression'},
  'lists_is_empty': {'argNames': ['LIST'], 'kind': 'expression'},
  'lists_length': {'argNames':['LIST'], 'kind': 'expression'},
  'lists_from_csv_row': {'argNames': ['TEXT'], 'kind': 'expression'},
  'lists_to_csv_row': {'argNames': ['LIST'], 'kind': 'expression'},
  'lists_from_csv_table': {'argNames': ['TEXT'], 'kind': 'expression'},
  'lists_to_csv_table': {'argNames': ['LIST'], 'kind': 'expression'},
  'lists_lookup_in_pairs': {'argNames': ['KEY', 'LIST', 'NOTFOUND'], 'kind': 'expression'},
  'lists_pick_random_item': {'argNames':['LIST'], 'kind': 'expression'},
  'lists_position_in': {'argNames':['ITEM', 'LIST'], 'kind': 'expression'},
  'lists_select_item': {'argNames': ['LIST', 'NUM'], 'kind': 'expression'},
  'lists_remove_item': {'argNames': ['LIST', 'INDEX'], 'kind': 'statement'},
  'lists_replace_item': {'argNames': ['LIST', 'NUM', 'ITEM'], 'kind': 'statement'},

  # Math

  'math_number': {'argNames': [], 'kind': 'expression'},
  'math_compare': {'argNames': ['A', 'B'], 'kind': 'expression'},
  'math_add': {'expandableArgName': 'NUM', 'kind': 'expression'},
  'math_add': {'expandableArgName': 'NUM', 'kind': 'expression'},
  'math_multiply': {'expandableArgName': 'NUM', 'kind': 'expression'},
  'math_subtract': {'argNames':['A', 'B'], 'kind': 'expression'},
  'math_division': {'argNames':['A', 'B'], 'kind': 'expression'},
  'math_power': {'argNames':['A', 'B'], 'kind': 'expression'},
  'math_random_int': {'argNames':['FROM', 'TO'], 'kind': 'expression'},
  'math_random_float': {'argNames':[], 'kind': 'expression'},
  'math_random_set_seed': {'argNames':['NUM'], 'kind': 'statement'},
  'math_single': {'argNames':['NUM'], 'kind': 'expression'},
  'math_abs': {'argNames':['NUM'], 'kind': 'expression'}, # Together with math_single                                   
  'math_neg': {'argNames':['NUM'], 'kind': 'expression'}, # Together with math_single                                   
  'math_round': {'argNames':['NUM'], 'kind': 'expression'}, # Together with math_single                                 
  'math_ceiling': {'argNames':['NUM'], 'kind': 'expression'}, # Together with math_single                               
  'math_floor': {'argNames':['NUM'], 'kind': 'expression'}, # Together with math_single                                 
  'math_divide': {'argNames':['DIVIDEND', 'DIVISOR'], 'kind': 'expression'},
  'math_on_list': {'expandableArgName': 'NUM', 'kind': 'expression'},
  'math_trig': {'argNames':['NUM'], 'kind': 'expression'},
  'math_cos': {'argNames':['NUM'], 'kind': 'expression'}, # Together with math_trig                                     
  'math_tan': {'argNames':['NUM'], 'kind': 'expression'}, # Together with math_trig                                     
  'math_atan2': {'argNames':['Y', 'X'], 'kind': 'expression'},
  'math_convert_angles': {'argNames':['NUM'], 'kind': 'expression'},
  'math_format_as_decimal': {'argNames':['NUM', 'PLACES'], 'kind': 'expression'},
  'math_is_a_number': {'argNames':['NUM'], 'kind': 'expression'},
  'math_convert_number': {'argNames':['NUM'], 'kind': 'expression'},

  # Strings/text                                                                                                       \
                                                                                                                        
  'text': {'argNames':[], 'kind': 'expression'},
  'text_join': {'expandableArgName': 'ADD', 'kind': 'expression'},
  'text_contains': {'argNames': ['TEXT', 'PIECE'], 'kind': 'expression'},
  'text_changeCase': {'argNames': ['TEXT'], 'kind': 'expression'},
  'text_isEmpty': {'argNames': ['VALUE'], 'kind': 'expression'},
  'text_compare': {'argNames': ['TEXT1', 'TEXT2'], 'kind': 'expression'},
  'text_length': {'argNames': ['VALUE'], 'kind': 'expression'},
  'text_replace_all': {'argNames': ['TEXT', 'SEGMENT', 'REPLACEMENT'], 'kind': 'expression'},
  'text_starts_at': {'argNames': ['TEXT', 'PIECE'], 'kind': 'expression'},
  'text_split': {'argNames': ['TEXT', 'AT'], 'kind': 'expression'},
  'text_segment': {'argNames': ['TEXT', 'START', 'LENGTH'], 'kind': 'expression'},
  'text_trim': {'argNames': ['TEXT'], 'kind': 'expression'}

}



# Maja's tests
# cleanup('/Users/Maja/Documents/AI/Tutorials', 'summary.json')
# projectToJSONFile('/Users/Maja/Documents/AI/PaintPot2Old.zip')
# allProjectsToJSONFiles('/Users/Maja/Documents/AI/Tutorials', 1000)
# findComponentType('hey', '/Users/Maja/Documents/AI/PaintPot2Old.zip', 'Screen1.scm')
#print upgradeFormat('Canvas_Clicked', '/Users/Maja/Documents/AI/PaintPot2Old.zip', 'Screen1.scm')


# Lyn's tests
# cleanup('/Users/fturbak/Projects/AppInventor2Stats/data/benji_ai2_users_random', '.zip')
# allProjectsToJSONFiles('/Users/fturbak/Projects/AppInventor2Stats/data/benji_ai2_users_random', 10)
# allProjectsToJSONFiles('/Users/fturbak/Projects/AppInventor2Stats/data/benji_ai2_users_random', 10003
# projectToJSONFile('/Users/fturbak/Projects/AppInventor2Stats/data/MIT-tutorials/HelloPurr.aia')
