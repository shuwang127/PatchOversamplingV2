import os
import re
import random

rootPath = './'
dataPath = rootPath + '/data/'
syntPath = rootPath + '/synthesis/'

_DEBUG_  = 0
_CHOICE_ = 8

def main():
    cnt = 0
    for root, ds, fs in os.walk(dataPath):
        for file in fs:
            # for each file.
            cnt += 1
            if _DEBUG_ & (cnt != 4): continue
            #-------------------------------------------------------------
            filename = os.path.join(root, file).replace('\\', '/')
            if not _DEBUG_: print(cnt, filename)
            lines = ReadPatch(filename)
            diffLines, atLines = FindDiffStartPoint(lines)
            ifLines = FindIfStats(lines)
            ifVLines = VerifyIfStats(lines, ifLines, atLines)
            for ifln in ifVLines:   # for each verified IF stat.
                for iCh in range(_CHOICE_):   # for each variant.
                    newLines = PatchOversampling(lines, atLines, ifln, nChoice=iCh)
                    newLines = ChangeLineNumbers(lines, diffLines, atLines, ifln, newLines)
                    SaveToFile(newLines, filename)
            # -------------------------------------------------------------
    return

def ReadPatch(filename):
    '''
    Read lines from the patch.
    :param filename:
    :return:
    '''

    fp = open(filename, encoding='utf-8', errors='ignore')  # get file point.
    lines = fp.readlines()  # read all lines.
    # numLines = len(lines)   # get the line number.
    # print(lines)

    if _DEBUG_:
        strLines = ''
        for i in range(len(lines)):
            strLines += str(i) + lines[i]
        print(strLines)

    return lines

def FindDiffStartPoint(lines):

    diffLines = [i for i in range(len(lines)) if lines[i].startswith('diff --git')]
    atLines = [i for i in range(len(lines)) if lines[i].startswith('@@ ')]
    if len(diffLines) == 0: print('[Error] <FindDiffStartPoint> diffLines is void.')
    if len(atLines) == 0: print('[Error] <FindDiffStartPoint> atLines is void.')
    if _DEBUG_: print('diffLines:', diffLines, '\natLines:', atLines)

    return diffLines, atLines

def FindIfStats(lines):

    # strLines = ''
    # for i in range(len(lines)):
    #     strLines += str(i) + lines[i]
    # print(strLines)

    ifLines = [i for i in range(len(lines)) if len(re.findall(r'if\s*\(', lines[i]))]
    if _DEBUG_: print('ifLines:', ifLines)

    return ifLines

def VerifyIfStats(lines, ifLines, atLines):

    # if stats should be in diff code.
    ifVLines = [ln for ln in ifLines if ln > atLines[0]]
    if _DEBUG_: print('ifVLines(s1):', ifVLines)

    # if stats should be in changed lines.
    ifVLines = [ln for ln in ifVLines if lines[ln].startswith('-') or lines[ln].startswith('+')]
    if _DEBUG_: print('ifVLines(s2):', ifVLines)

    # if stats should have the corresponding ).
    ifVLinesFinal = []
    # print(atLines)
    for ifln in ifVLines:
        lnEnd = [ln for ln in atLines if ln > ifln]
        lnEnd = lnEnd[0] if (len(lnEnd)) else len(lines)
        # print(lnEnd)
        strLines = ''
        for i in range(ifln, lnEnd):
            strLines += lines[i]
        # print(strLines)
        # locate if_(*)
        ifStart = re.findall(r'if\s*\(', strLines)
        indexIfStart = strLines.index(ifStart[0])
        indexIfLeft = indexIfStart + len(ifStart[0]) - 1
        indexIfRight = indexIfLeft
        mark = 1
        while (mark):
            indexIfRight += 1
            if (indexIfRight == len(strLines)): break
            if strLines[indexIfRight] == '(':
                mark += 1
            elif strLines[indexIfRight] == ')':
                mark -= 1
        if _DEBUG_: print(indexIfStart, indexIfLeft, indexIfRight)
        # ---------------------------------------------------------------
        # if stats if(*) should have the same diff-sign for each line.
        # if _DEBUG_: print(strLines[:indexIfRight+1])
        numEnter = strLines[:indexIfRight + 1].count('\n')
        numEnterSign = strLines[:indexIfRight + 1].count('\n'+strLines[0])
        if _DEBUG_: print(numEnter, numEnterSign)
        mark = 1 if (numEnter == numEnterSign) else 0
        # ---------------------------------------------------------------
        if (indexIfRight != len(strLines)) & (mark):
            ifVLinesFinal.append(ifln)

    if _DEBUG_: print('ifVLines(s3):', ifVLinesFinal)

    return ifVLinesFinal

def PatchOversampling(lines, atLines, ifln, nChoice=-1):
    '''
    Patch oversampling with different options.
    :param lines:
    :param atLines:
    :param ifln:
    :param nChoice:
    :return:
    '''

    # get the font part.
    newLines = lines[0:ifln]
    # print(newLines)

    # convert the middle part into string.
    lnEnd = [ln for ln in atLines if ln > ifln]
    lnEnd = lnEnd[0] if (len(lnEnd)) else len(lines)
    strLines = ''
    for i in range(ifln, lnEnd):
        strLines += lines[i]
    # print(strLines)

    # locate the if_(*) statement in the middle part.
    ifStart = re.findall(r'if\s*\(', strLines)
    indexIfStart = strLines.index(ifStart[0])
    indexIfLeft = indexIfStart + len(ifStart[0]) - 1
    indexIfRight = indexIfLeft
    mark = 1
    while (mark):
        indexIfRight += 1
        if (indexIfRight == len(strLines)): break
        if strLines[indexIfRight] == '(':
            mark += 1
        elif strLines[indexIfRight] == ')':
            mark -= 1
    if _DEBUG_: print(indexIfStart, indexIfLeft, indexIfRight)

    # change the patch with different choice settings.
    if (nChoice not in range(_CHOICE_)):        # if nChoice is not in our settings.
        nChoice = random.randint(0, _CHOICE_-1) # randomly choose.
    newstrLines = ''
    if (0 == nChoice):  # add 1, modify 1
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'const int _SYS_ZERO = 0; \n'
        newstrLines += strLines[:indexIfLeft + 1] + '_SYS_ZERO || ' + strLines[indexIfLeft + 1:]
    elif (1 == nChoice):  # add 1, modify 1
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'const int _SYS_ONE = 1; \n'
        newstrLines += strLines[:indexIfLeft + 1] + '_SYS_ONE && ' + strLines[indexIfLeft + 1:]
    elif (2 == nChoice): # add 1, modify n
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'bool _SYS_STMT = ' + strLines[indexIfLeft+1:indexIfRight] + ';\n'
        newstrLines += strLines[:indexIfLeft+1] + 'True == _SYS_STMT' + strLines[indexIfRight:]
    elif (3 == nChoice): # add 1, modify n
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'bool _SYS_STMT = !(' + strLines[indexIfLeft + 1:indexIfRight] + ');\n'
        newstrLines += strLines[:indexIfLeft + 1] + '!_SYS_STMT' + strLines[indexIfRight:]
    elif (4 == nChoice): # add n+3, modify 1
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'int _SYS_VAL = 0;\n'
        newstrLines += strLines[:indexIfRight+1] + ' {\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart+3) + 'int _SYS_VAL = 1;\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) +'}\n'
        newstrLines += strLines[:indexIfLeft+1] + '_SYS_VAL && ' + strLines[indexIfLeft+1:]
    elif (5 == nChoice): # add n+3, modify 1
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'int _SYS_VAL = 1;\n'
        newstrLines += strLines[:indexIfRight + 1] + ' {\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart+3) + 'int _SYS_VAL = 0;\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + '}\n'
        newstrLines += strLines[:indexIfLeft+1] + '!_SYS_VAL || ' + strLines[indexIfLeft+1:]
    elif (6 == nChoice): # add 4, modify n
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'int _SYS_VAL = 0;\n'
        newstrLines += strLines[:indexIfRight + 1] + ' {\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart+3) + 'int _SYS_VAL = 1;\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + '}\n'
        newstrLines += strLines[:indexIfLeft+1] + '_SYS_VAL' + strLines[indexIfRight:]
    elif (7 == nChoice): # add 4, modify n
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + 'int _SYS_VAL = 1;\n'
        newstrLines += strLines[:indexIfRight + 1] + ' {\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart+3) + 'int _SYS_VAL = 0;\n'
        newstrLines += strLines[0] + ' ' * (indexIfStart-1) + '}\n'
        newstrLines += strLines[:indexIfLeft + 1] + '!_SYS_VAL' + strLines[indexIfRight:]
    # print(newstrLines)

    # change string to lists.
    newlistLines = newstrLines.split('\n')
    newlistLines = [stmt + '\n' for stmt in newlistLines[:-1]]
    # print(newlistLines)

    # combine the front part, middle part, and latter part.
    newLines.extend(newlistLines)
    newLines.extend(lines[lnEnd:])
    # print(newLines)

    strLines = ''
    for i in range(len(newLines)):
        strLines += newLines[i]
    if _DEBUG_: print(strLines)
    if _DEBUG_: print(len(lines), len(newLines), len(newLines)-len(lines))

    return newLines

def ChangeLineNumbers(lines, diffLines, atLines, ifln, newLines):
    '''
    Change the corresponding line numbers in the @-lines.
    :param lines:
    :param diffLines:
    :param atLines:
    :param ifln:
    :param newLines:
    :return:
    '''

    # count the number of line changed.
    numChanged = len(newLines) - len(lines)
    if (0 == numChanged):
        return newLines
    # find the sign before the if stat.
    signChg = lines[ifln][0]
    offset = 0 if (signChg == '-') else 2

    # get the start atlines.
    lnStart = [ln for ln in atLines if ln < ifln][-1]
    # get the last diffline.
    lnEnd = [ln for ln in diffLines if ln > ifln]
    lnEnd = lnEnd[0] if (len(lnEnd)) else len(lines)
    # get the atLines need to change in newLines.
    atLinesChg = [ln for ln in atLines if (ln >= lnStart) & (ln < lnEnd)]
    for i in range(1, len(atLinesChg)):
        atLinesChg[i] += numChanged
    # print(lnStart, lnEnd, atLinesChg)

    for ln in atLinesChg:
        # get the @-line.
        line = newLines[ln]
        if _DEBUG_: print(line)
        # sparse the @@ -000,00 +000,00 @@.
        atStmt = re.findall(r'@@ -\d+,\d+ \+\d+,\d+ @@', line)[0]
        atNum = re.findall(r'\d+', atStmt)  # get 4 numbers
        lnList = [int(atNum[0]), int(atNum[1]), int(atNum[2]), int(atNum[3])]
        # change the list number.
        if _DEBUG_: print(lnList)
        lnList[offset+1] += numChanged
        if (ln != atLinesChg[0]):
            lnList[offset+0] += numChanged
        if _DEBUG_: print(lnList)
        # reconstruct the line.
        atRepr = '@@ -' + str(lnList[0]) + ',' + str(lnList[1]) + ' +' + str(lnList[2]) + ',' + str(lnList[3]) + ' @@'
        line = line.replace(atStmt, atRepr, 1)
        if _DEBUG_: print(line)
        # substitute the @-line.
        newLines[ln] = line

    return newLines

def SaveToFile(newLines, filename):

    # sparse the original filename.
    (path, file) = os.path.split(filename)
    # print(path, file)

    # construct new path.
    newPath = path.replace(dataPath, syntPath)
    # print(newPath)
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    # find an available name.
    #fileList = os.listdir(newPath)
    fileIdx = 1
    while (1):
        fname = file + '.' + str(fileIdx).zfill(5)
        if not os.path.exists(os.path.join(newPath, fname)):
            break
        else:
            fileIdx += 1
    fpath = os.path.join(newPath, fname).replace('\\', '/')

    # save file.
    fp = open(fpath, 'w')
    for i in range(len(newLines)):
        fp.write(newLines[i].encode("gbk", 'ignore').decode("gbk", "ignore"))
    fp.close()
    if _DEBUG_: print('[DEBUG] Save patch variant in ' + fpath)

    return fpath

if __name__ == '__main__':
    main()