
import re
import pandas as pd
import sys
import subprocess
import glob
from os.path import join
def loadSW2IDX(SW2Afilepath):#sw2idx_1226test_v5
     #load keyword sets
    symboleItem = {} #for +繳費 
    allsubkey = []
    keyworddict = {}
    with open(SW2Afilepath,'r',encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            subkeyword = line#.lower()
            allsubkey.append(subkeyword)
            symbollist =  re.findall('([^一-龥A-Za-z]+)',subkeyword)
            if symbollist:
                replaceitem = subkeyword.replace('+','').replace('-','')
                allsubkey.append(replaceitem)
                #glue chinese and a-z
                if replaceitem in symboleItem:
                    if not symboleItem[replaceitem] == subkeyword:
                        print('oh! something wrong',symboleItem[replaceitem],subkeyword)
                symboleItem[replaceitem] = subkeyword

    return {},list(set(allsubkey)),symboleItem
def loadKW2SKW(SW2Afilepath):
    #load keyword sets
    symboleItem = {} #for +繳費 
    allsubkey = []
    keyworddict = {}
    with open(SW2Afilepath,'r',encoding='utf8') as f:
        for line in f.readlines():
            linelist = line.strip().split('\t')
            #if len(re.findall('([A-Za-z]+)',linelist[2])) > 0:
            #    print(linelist[2])
            subkeywordlist = linelist[2].split(' ')
            subkeywordsum = int(linelist[1])
            motherkeyword = linelist[0].lower()
            keyworddict[motherkeyword] = []
            #[keyworddict[motherkeyword].append(subkeywordlist[i].lower().replace('+','').replace('-','')) for i in range(subkeywordsum)]
            for i in range(subkeywordsum):
                symbollist =  re.findall('([^一-龥A-Za-z]+)',subkeywordlist[i].lower())
                subkeyword = subkeywordlist[i].lower()
                # if '門號轉移' in subkeyword:
                #     print('in')
                # oriitem = subkeyword
                # for item in re.findall('([一-龥]+ [A-Za-z]+)',subkeyword):
                #     subkeyword = subkeyword.replace(item,item.replace(' ',''))
                # for item in re.findall('([A-Za-z]+ [一-龥]+)',subkeyword):
                #     subkeyword = subkeyword.replace(item,item.replace(' ',''))
                # if not oriitem == subkeyword:
                #     print(oriitem,subkeyword)
                if symbollist:
                    replaceitem = subkeyword.replace('+','').replace('-','')
                    #glue chinese and a-z
                    if replaceitem in symboleItem:
                        if not symboleItem[replaceitem] == subkeyword:
                            print('oh! something wrong',symboleItem[replaceitem],subkeyword)
                    symboleItem[replaceitem] = subkeyword
                    keyworddict[motherkeyword].append(replaceitem)
                else:
                    keyworddict[motherkeyword].append(subkeyword)
            
            allsubkey.extend(keyworddict[motherkeyword])
            
    return keyworddict,list(set(allsubkey)),symboleItem
def recursive_subKey(thissubkey,othersubkeylist,inputStr,thisSets,groupSets):
   
    if thissubkey in othersubkeylist:
        othersubkeylist.remove(thissubkey)
    #if len(thissubkey) > len(inputStr.replace(' ','')):
    #    return 'length too long'
    if thissubkey in inputStr:
        thisSets.append(thissubkey)
        inputStr = inputStr.replace(thissubkey,' ')
        #print('string',inputStr)
    if len(re.findall(r'\S',inputStr)) == 0:
        groupSets.append(thisSets)
        #print('no more, thisSets:',thisSets)
        return 'no more'
    inflag = False
    
    candidate = []
    for subkey in othersubkeylist:
        if subkey in inputStr:
            inflag = True
            candidate.append(subkey)
    possiblecnt = 0
    for subkey in candidate:
        possiblecnt+=1
        #print(possiblecnt,subkey,'inputStr:',inputStr,thisSets,groupSets)
        recursive_subKey(subkey,candidate.copy(),inputStr,thisSets.copy(),groupSets)

    if not inflag:
        #print('no in, thisSets:',thisSets)
        groupSets.append(thisSets)
        return 'no more'
   
def generatesub(inputStr,allsubkey):
    
    allGroup = {}
    for subkey in allsubkey:
        #print(subkey)
        
        allGroup[subkey] = []
        thisSets = []
        recursive_subKey(subkey, allsubkey.copy(), inputStr, thisSets,allGroup[subkey])
        #print('=================')
    return allGroup
def getAllpossible(inputString,allsubkey,symboleItem):
    
    if str(inputString) == 'nan':
        return []
    inputString = inputString.lower()
    allcandidateSubdict = {}
    for subkey in allsubkey:
        if subkey in inputString:
            allcandidateSubdict[subkey] = len(subkey)
        elif subkey.lower() in inputString:
            allcandidateSubdict[subkey.lower()] = len(subkey)

    allcandidateSubdict = sorted(allcandidateSubdict.items(), key=lambda kv: kv[1],reverse=True)
    allcandidateSub = [allcandidateSubdict[i][0] for i in range(len(allcandidateSubdict))]
    allcandidateSub = [item for item in allcandidateSub if len(item) > 1] # ger rid of single word
    
    
    #print(inputString,allcandidateSub) #debug use
    
    allGroup = generatesub(inputString,allcandidateSub)
    #print(allGroup) #debug use
    allpossible = []
    for key,groups in allGroup.items():   
        for group in groups:
            #print(group)
            allocate = {}
            newgroup = []
            usedIndex = []
            for item in group:
                indexList = [m.start() for m in re.finditer(item,inputString)]
                if len(indexList) == 1:
                    allocate[indexList[0]] = item
                    usedIndex.append(indexList[0])
                else:
                    
                    for index in usedIndex:
                        try:
                            indexList.remove(index)
                        except:
                            print(item,inputString,indexList,usedIndex)
                    if len(indexList) == 1:
                        allocate[indexList[0]] = item
                        usedIndex.append(indexList[0])
                    else:
                        allocate[indexList[0]] = item
                        usedIndex.append(indexList[0])
            for item in sorted(allocate.items(), key=lambda kv: kv[0]):
                # if item[1] in fillerList: # 
                #     continue
                if item[1] in symboleItem:
                    newgroup.append(symboleItem[item[1]])
                else:
                    newgroup.append(item[1])
            if newgroup:
                allpossible.append(' '.join(newgroup))
    goalList = list(set(allpossible))
    rmGoalList = goalList[:]
    otherSets = goalList.copy()
    for possible in goalList:
        otherSets.remove(possible)
        for other in otherSets:
            possibleLen = len(possible.split(' '))
            if  possibleLen == len(other.split(' ')):
                allIn = True
                if len(possible) > len(other):
                    shorterOne = other.split(' ')
                    longerOne = possible.split(' ')
                else:
                    shorterOne = possible.split(' ')
                    longerOne = other.split(' ')
                for i in range(possibleLen):
                    if not shorterOne[i] in longerOne[i]:
                        allIn = False
                if allIn:
                    if ' '.join(shorterOne) in rmGoalList:
                        rmGoalList.remove(' '.join(shorterOne))
                    # print(shorterOne,'in',longerOne) #debug
                #for kw in possible.split(' '):
                #    other.split(' ')
                # print(possible,other,'PK') #debug
    # if rmGoalList != sorted(rmGoalList, key=len):
    #     print(rmGoalList,sorted(rmGoalList, key=len))
    rmMoveList = []
    if len(rmGoalList) > 1:
        for item in rmGoalList:
            if '+' in item or '-' in item:
                pass
            else:
                rmMoveList.append(item)
    if rmMoveList:
        rmGoalList = sorted(rmMoveList, key=len)    
    else:
        rmGoalList = sorted(rmGoalList, key=len)   
    locationDict = {}
    try:
        for item in rmGoalList:
            locationDict[item] = inputString.index(item[0].replace('+','').replace('-',''))
    except:
        print('ininder')
    locationDictSort = sorted(locationDict.items(), key=lambda k: k[1])
    rmGoalList = [locationDictSort[i][0] for i in range(len(locationDictSort))]
    return rmGoalList#rmGoalList
def caculate_thisturnpossibleKeyword(allpossibleList,ASRkeywordList,allsubkey):
    matchPossible = {}
    minLen = 5
    minLenpossible = ''
    thisturnpossibleKeyword = ''
    if len(allpossibleList) > 1:
        #print(inStr, allpossibleList)
        for possible in allpossibleList:
            possibleList = possible.split(' ') 
            if len(possibleList) < minLen:
                minLen = len(possibleList)
                minLenpossible = possibleList
            incount = 0
            for asrkey in ASRkeywordList:
                if asrkey in possibleList:
                    incount+=1
            matchPossible[possible] = incount
        sortmatchPossible = sorted(matchPossible.items(), key=lambda k: k[1], reverse = True)
        if sortmatchPossible[0][1] == 0:
            thisturnpossibleKeyword = ' '.join(minLenpossible)
        else:
            thisturnpossibleKeyword = sortmatchPossible[0][0]
            
        #choose incount max and length max(get rid of ' ')
    else:
        if len(allpossibleList)>0:
            thisturnpossibleKeyword = allpossibleList[0]
    resultThisTurn = []
    if not thisturnpossibleKeyword == '':
        for item in thisturnpossibleKeyword.split(' '):
            if not item in allsubkey:
                if item.upper() in allsubkey:
                    resultThisTurn.append(item.upper())
                else:
                    print(item,'WOWOWOW')
            else:
                resultThisTurn.append(item)
    if resultThisTurn:
        return ' '.join(resultThisTurn)
    else:
        return thisturnpossibleKeyword
def getUnlist(inStr,thisturnpossibleKeyword,intersection,fillerList):
    checkStr = str(inStr)[:]
    for item in intersection:
        checkStr = checkStr.replace(item,' ')
        checkStr = checkStr.replace(item.replace('+','').replace('-',''),' ')
    checkStrListStr = ' '.join(checkStr.split(' '))
    
    for item in thisturnpossibleKeyword.split(' '):
        if item in checkStrListStr:
            checkStrListStr = checkStrListStr.replace(item,' ')
        elif item.upper() in checkStrListStr:
            checkStrListStr = checkStrListStr.replace(item.upper(),' ')
        elif item.lower() in checkStrListStr:
            checkStrListStr = checkStrListStr.replace(item.lower(),' ')
        elif item.replace('+','').replace('-','') in checkStrListStr:
            checkStrListStr = checkStrListStr.replace(item.replace('+','').replace('-',''),' ')
    newcheckStrList = []
    for item in checkStrListStr.split(' '):
        if item in fillerList or item == '':
            pass
        else:
            newcheckStrList.append(item)
    return newcheckStrList
def leafnodeSearch(itemList,idxtable):
    seachList = []
    for item in itemList:
        if item in idxtable:
            seachList.append('sw'+str(idxtable.index(item)+1))
        elif item.upper() in idxtable:
            seachList.append('sw'+str(idxtable.index(item.upper())+1))
        elif item.lower() in idxtable:
            seachList.append('sw'+str(idxtable.index(item.lower())+1))

    cmd = 'echo' + ' "'+';'.join(seachList)+'"'+'| awk -f sw2a.awk'
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    result = output.decode("utf-8")
    return result.split('\t')[0].split(':')[1].split(';')

def main():
    idxfilepath = 'sw2idx'
    idxtable = []
    with open(idxfilepath,'r',encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            idxtable.append(line)
    fillerList = ['我要' ,'我想' ,'我想要' ,'請幫我' ,'我要換' ,'我要訂' ,'我要看' ,'我要拿' ,'我要對' ,'我想找' ,'補印' ,'的票' ,'有沒有']
    #keyworddict,allsubkey,symboleItem = loadKW2SKW('sw2a_1206v1.xlsx.csv-step3.words')
    keyworddict,allsubkey,symboleItem = loadSW2IDX(idxfilepath)#sw2idx_1226test_v5)
    allsubkey.extend(['臺灣','臺鐵','臺北','臺中','臺南','臺東','台灣','台鐵','台北','台中','台南','台東'])
    allsubkey = list(set(allsubkey))
    
    
    #print(symboleItem)
    #if 'card' in allsubkey:
    #    print('inin')
    #print(keyworddict)
    #print(getAllpossible('A:台灣大車隊B:(欸)台灣大車隊',allsubkey,symboleItem))
    #sys.exit()
    #load excel
    for excelfile in glob.glob(join('inputexcel','*')):
        if 'result' in excelfile:
            continue
        print(excelfile)
        df = pd.read_excel(excelfile)#,header=None
        ouputfilename = excelfile.replace('.xlsx','result')
        compareExcelfile = ouputfilename
        compareString = ''#'賞櫻專車票券'
        symbolList = []

        #check it there any symbol out of [^一-龥A-Za-z]
        for ASRresult in df['ASR辨識結果'].tolist():
            if ASRresult == '無偵測到關鍵字' or ASRresult == 'NoVoiceIn':
                pass
            else:
                ASRkeywordList = [item for item in re.sub(r'\[\d+\]','',ASRresult).split('_')]
                for item in ASRkeywordList:
                    symbol = re.findall('([^一-龥A-Za-z]+)',item)
                    symbolList.extend(symbol)
        
        print(set(symbolList))
        accurancy = []
        subkeyword = []
        matchKeywordList = []
        subStrPossible = []
        mostpossibleKeyword = []
        unlistList = []
        for i in range(len(df)):
            inStr = str(df.iloc[i]['標記逐字稿'])
            status = str(df.iloc[i]['狀態'])
            if inStr == '蝦皮寄件，蝦皮寄':
                print(inStr)
            
            
            if '[台' in inStr:
                twLens = [m.group(1) for m in re.finditer(r'\[台(\d+)\]',inStr)]
                twEnds = [m.end() for m in re.finditer(r'\[台(\d+)\]',inStr)]
                tmpindex = 0
                twSenList = []
                for each in twLens:
                    twSentence = '[台'+each+']'+inStr[int(twEnds[tmpindex]):int(twEnds[tmpindex])+int(each)]
                    twSenList.append(twSentence)
                    tmpindex+=1
                for item in twSenList:
                    inStr = inStr.replace(item,'')
                if inStr == '':
                    inStr = 'nan'
            for item in (re.findall(r'\(.+\)',inStr)):
                inStr = inStr.replace(item,'')
            ASRresult = df.iloc[i]['ASR辨識結果']#1226NG ASR結果
            ASRkeywordList = [item.lower() for item in re.sub(r'\[\d+\]','',ASRresult).split('_')]
            

            # humanListenAction = str(df.iloc[i]['逐字稿斷詞語意結果'])
            # ASRAction = str(df.iloc[i]['ASR辨識語意結果'])
            allpossibleList = getAllpossible(inStr,allsubkey,symboleItem)
            
            subkeyword.append(','.join(allpossibleList))
            
            ASRserviceList = []
            thisturnpossibleKeyword = caculate_thisturnpossibleKeyword(allpossibleList,ASRkeywordList,allsubkey)
            
            
            if ':' in str(inStr):
                subStrPossible.append('')
                matchKeywordList.append('')
                mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
                unlistList.append('')
                accurancy.append('不列入(對話)')
            elif status == '3':
                subStrPossible.append('')
                matchKeywordList.append('')
                mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
                unlistList.append('')
                accurancy.append('待討論(狀態三)')
            elif status == '11':
                subStrPossible.append('')
                matchKeywordList.append('')
                mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
                unlistList.append('')
                accurancy.append('不列入(狀態十一)')
            elif ASRresult == '無偵測到關鍵字':
                subStrPossible.append('')
                matchKeywordList.append('')
                mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
                newcheckStrList = getUnlist(inStr,thisturnpossibleKeyword,[],fillerList)
                if not allpossibleList: # or only filler
                    if not inStr == 'nan':
                        # if newcheckStrList:
                        #     unlistList.append('無語意詞-'+','.join(newcheckStrList))
                        # else:
                        #     unlistList.append('')
                        unlistList.append('無語意詞-'+inStr)
                        accurancy.append('是') #ASR true
                    else:
                        unlistList.append('')
                        accurancy.append('是') #ASR true
                    #print('yes','no sub keyword','無偵測到關鍵字')
                else:
                    
                    # unlisttmp = []
                    # for item in allpossibleList:
                    #     if not item in allsubkey and not item.upper in allsubkey:
                    #         unlisttmp.append(item)
                    #newcheckStrList = getUnlist(inStr,thisturnpossibleKeyword,[],fillerList)
                    accurancy.append('否')
                    if newcheckStrList:
                        unlistList.append('無語意詞-'+','.join(newcheckStrList))
                    else:
                        unlistList.append('')
                    # else:
                    #     accurancy.append('是(只有filler)')
                    
            elif ASRresult == 'NoVoiceIn':
                subStrPossible.append('')
                matchKeywordList.append('')
                mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
                unlistList.append('')
                if str(inStr) == 'nan':
                    accurancy.append('是(NoVoiceIn)')
                    #print('yes',ASRresult)
                    
                else: #ASR False
                    if not allpossibleList:
                        accurancy.append('不列入(NoVoiceIn)')
                    else:
                        accurancy.append('否')
            else:
                #for y in list(set(symbolList)):
                #    ASRkeywordList = [item[:-4].replace(y,'') for item in ASRresult.split('_')]
                
                ASRkeywordList = list(set(ASRkeywordList))
                #ASRkeywordList = [item[:-4].lower() for item in ASRresult.split('_')]
                # for item in ASRkeywordList:
                #     noSymbolitem = item.replace('+','').replace('-','') # check all symbol here!!
                #     if noSymbolitem in fillerList:
                #         ASRkeywordList.remove(item)
                sortallpossibleList = [sorted(item) for item in allpossibleList]
                if sorted(' '.join(ASRkeywordList)) in sortallpossibleList:
                    #ASRkeywordList = [item[:-4] for item in ASRresult.split('_')]
                    accurancy.append('是')
                    matchKeywordList.append(' '.join(ASRkeywordList))
                    mostpossibleKeyword.append(';'.join(ASRkeywordList))
                    subStrPossible.append('')
                    unlistList.append('')
                    # if not humanListenAction == ASRAction:
                    #     #pass
                    #     print('check!! Not same Action')
                        #print(allpossibleList,inStr)
                    #print('yes',allpossibleList,ASRkeywordList)
                elif len(thisturnpossibleKeyword.split(' '))== 1 and '+' in thisturnpossibleKeyword:
                    subStrPossible.append('')
                    matchKeywordList.append('')
                    mostpossibleKeyword.append('')
                    unlistList.append('')
                    accurancy.append('不列入(只有動詞)')
                else:
                    
                    mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
                    matchKeywordList.append('')
                    inStr = re.sub(r'(\(.+\))','',str(inStr))
                    if not allpossibleList:
                        accurancy.append('不列入')
                        if inStr == '' or inStr == 'nan':
                            unlistList.append('')
                        else:
                            for filler in fillerList:
                                inStr = inStr.replace(filler,'')
                            unlistList.append('無語意詞-'+inStr)
                        subStrPossible.append('')
                    
                    else:
                        subStrPossible.append('')

                        # if humanListenAction == ASRAction:
                        #     #print('change') KPI!
                        #     accurancy.append('是(語意相同)')
                        #     unlistList.append('')
                        # else:
                        intersection = list(set(ASRkeywordList).intersection(set(thisturnpossibleKeyword.split(' '))))
                        newcheckStrList = getUnlist(inStr,thisturnpossibleKeyword,intersection,fillerList)
                        
                        thisUnlist = ''
                        if newcheckStrList:
                            thisUnlist = '無語意詞-'+','.join(newcheckStrList)
                        else:
                            thisUnlist = ''
                        #check humanListenAction is leaf node or not
                        """
                        C: 正確辨識語意詞集合、D: 錯誤刪減語意詞集合、I: 錯誤加入語意詞集合、S: 標準答案語意詞集合、R: 辨識結果語意詞集合
                        S = C+D humanListenAction_Nodes
                        R = C+I ASRAction_Nodes
                        """
                        #print(humanListenAction,ASRAction)
                        #print(inStr)
                        ASRAction_Nodes = leafnodeSearch(ASRkeywordList,idxtable)
                        humanListenAction_Nodes = leafnodeSearch(thisturnpossibleKeyword.split(' '),idxtable)
                        
                        # humanListenAction_Nodes = re.findall('[LB];([一-龥]+)',humanListenAction)
                        # ASRAction_Nodes = re.findall('[LB];([一-龥]+)',ASRAction)
                        #actionIntersection = list(set(humanListenAction_Nodes).intersection(set(ASRAction_Nodes)))
                        actionIntersection = list(set(ASRAction_Nodes).intersection(set(humanListenAction_Nodes)))
                        if len(ASRAction_Nodes) == 1:#'已為您連結至' in ASRAction: # |L(R)|=1 
                            if len(humanListenAction_Nodes) == 1:#'已為您連結至' in humanListenAction:
                                if set(ASRAction_Nodes) == set(humanListenAction_Nodes):
                                    #2.1.1
                                    accurancy.append('是( |L(S)|=1,|L(R)|=1 L(R) = L(S)')
                                    unlistList.append(thisUnlist)
                                else:
                                    #2.1.2
                                    accurancy.append('否( |L(S)|=1,|L(R)|=1 L(R) ≠ L(S)')
                                    unlistList.append(thisUnlist)
                            else: 
                                #2.2.1	If L(R) ⊄ L(S)，則應算N
                                if not set(actionIntersection) == set(humanListenAction_Nodes) :
                                    accurancy.append('否( |L(S)|>1,|L(R)|=1  L(R) ⊄ L(S)')
                                    unlistList.append(thisUnlist)
                                else:
                                    #2.2.2
                                    accurancy.append('討論( |L(S)|>1,|L(R)|=1 使用者意圖不清')
                                    unlistList.append(thisUnlist)
                                
                        else:# |L(R)| > 1 
                            if len(humanListenAction_Nodes) == 1:
                                #2.4
                                if set(humanListenAction_Nodes) == set(actionIntersection):
                                    #2.4.1
                                    accurancy.append('是( |L(S)|=1,|L(R)|>1  L(S) ⊂ L(R)')
                                    unlistList.append(thisUnlist)
                                else:
                                    #2.4.2
                                    accurancy.append('否( |L(S)|=1,|L(R)|>1  ')
                                    unlistList.append(thisUnlist)
                                    #print('N |L(R)|>1,|L(S)|=1,L(S) ∩ L(R) = φ')
                            else:
                                #2.3
                                if set(ASRAction_Nodes) == set(humanListenAction_Nodes):
                                    #2.3.1
                                    accurancy.append('是( |L(S)|>1,|L(R)|>1 L(S) = L(R)')
                                    unlistList.append(thisUnlist)
                                elif set(actionIntersection) == set(humanListenAction_Nodes) :
                                    #2.3.2
                                    accurancy.append('是( |L(S)|>1,|L(R)|>1 L(S) ⊂ L(R)')
                                    unlistList.append(thisUnlist)
                                else:
                                    #2.3.3
                                    if actionIntersection:
                                        accurancy.append('否( |L(S)|>1,|L(R)|>1 L(S) ∩ L(R) ≠ φ')
                                        unlistList.append(thisUnlist)
                                    else:
                                        accurancy.append('否( |L(S)|>1,|L(R)|>1 L(S) ∩ L(R) = φ')
                                        unlistList.append(thisUnlist)
            if len(accurancy) != len(subkeyword):
                print(inStr)
                sys.exit()

        df['accuracy'] = accurancy
        df['subkeyword'] = subkeyword
        df['matchKeyword'] = matchKeywordList
        df['subStrPossible'] = subStrPossible
        df['mostpossibleKeyword'] = mostpossibleKeyword
        df['unlistList'] = unlistList
        #df1 = df[['標記逐字稿','ASR辨識結果','subkeyword','逐字稿斷詞結果','matchKeyword','mostpossibleKeyword','accuracy','語音辨識是否正確','unlistList']]
        df1 = df[['標記逐字稿','ASR辨識結果','subkeyword','matchKeyword','mostpossibleKeyword','accuracy','語音辨識是否正確','unlistList']]
        
        writer = pd.ExcelWriter(ouputfilename,engine='xlsxwriter')
        df1.to_excel(writer,'Sheet1')

        writer.save()
        df = pd.read_excel(compareExcelfile)#,header=None
        if not compareString == '':
            print(df[df['標記逐字稿'] == compareString]['subkeyword'])
            print(df[df['標記逐字稿'] == compareString].mostpossibleKeyword)
    #print(df.head())
    # inputString = '不鏽鋼保溫壺'
    # allpossibleList = getAllpossible(inputString,allsubkey)
    # print(allpossibleList)

    #get candidate subkeywords in loadKW2SKW_SRC
    

if __name__ =='__main__':
    main()