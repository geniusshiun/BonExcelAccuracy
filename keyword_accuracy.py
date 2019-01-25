
import re
import pandas as pd
import sys
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
            for item in group:
                index = [m.start() for m in re.finditer(item,inputString)][0]
                allocate[index] = item
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
    return sorted(rmGoalList, key=len)#rmGoalList
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
def main():
    fillerList = ['我要' ,'我想' ,'我想要' ,'請幫我' ,'我要換' ,'我要訂' ,'我要看' ,'我要拿' ,'我要對' ,'我想找' ,'補印' ,'的票' ,'有沒有']
    #keyworddict,allsubkey,symboleItem = loadKW2SKW('sw2a_1206v1.xlsx.csv-step3.words')
    keyworddict,allsubkey,symboleItem = loadSW2IDX('sw2idx_0119v6')#sw2idx_1226test_v5)
    allsubkey.extend(['臺灣','臺鐵','臺北','臺中','臺南','臺東','台灣','台鐵','台北','台中','台南','台東'])
    allsubkey = list(set(allsubkey))
    ouputfilename = 'iBon0107report.xlsx'
    #print(symboleItem)
    #if 'card' in allsubkey:
    #    print('inin')
    #print(keyworddict)
    #print(getAllpossible('A:台灣大車隊B:(欸)台灣大車隊',allsubkey,symboleItem))
    #sys.exit()
    #load excel
    df = pd.read_excel('語音互動詢答0107_0108(iBonPWSTD_stage3_20190119_NG)_0119YH(新版LM).xlsx')#,header=None
    symbolList = []

    #check it there any symbol out of [^一-龥A-Za-z]
    for i in range(len(df)):
        ASRresult = df.iloc[i]['ASR辨識結果']
        
        if ASRresult == '無偵測到關鍵字':
            pass
        else:
            ASRkeywordList = [item[:-4] for item in ASRresult.split('_')]
    for item in ASRkeywordList:
        symbol = re.findall('([^一-龥A-Za-z]+)',item)
        symbolList.extend(symbol)
    
    #print(set(symbolList))

    accurancy = []
    subkeyword = []
    matchKeywordList = []
    subStrPossible = []
    mostpossibleKeyword = []
    unlistList = []
    # inStr = '勞動部勞工保險局保險費繳款'
    # for i in range(100):
    #     allpossibleList = getAllpossible(inStr,allsubkey,symboleItem)
    #     thisturnpossibleKeyword = caculate_thisturnpossibleKeyword(allpossibleList,ASRkeywordList,allsubkey)
        
    #     print(allpossibleList,thisturnpossibleKeyword)
    # sys.exit()
    for i in range(len(df)):
        inStr = str(df.iloc[i]['標記逐字稿'])
        if inStr == '勞動部勞工保險局保險費繳款':
            print(inStr)
        ASRresult = df.iloc[i]['ASR辨識結果']#1226NG ASR結果
        humanListenAction = str(df.iloc[i]['逐字稿斷詞語意結果'])
        ASRAction = str(df.iloc[i]['ASR辨識語意結果'])
        allpossibleList = getAllpossible(inStr,allsubkey,symboleItem)
        
        subkeyword.append(','.join(allpossibleList))
        serviceList = re.findall('已為您連結至(.+)的(.+)服務',humanListenAction)
        ASRserviceList = []
        ASRkeywordList = [item[:-4].lower() for item in ASRresult.split('_')]
        if '」還是「' in ASRAction:
            ASRserviceList = re.findall('「(.+)」',ASRAction)
            ASRserviceList = ASRserviceList[0].split('」還是「')
            #print(ASRserviceList)
        
        if ':' in str(inStr):
            subStrPossible.append('')
            matchKeywordList.append('')
            mostpossibleKeyword.append('')
            unlistList.append('')
            accurancy.append('不列入(對話)')
        
        elif ASRresult == '無偵測到關鍵字':
            subStrPossible.append('')
            matchKeywordList.append('')
            thisturnpossibleKeyword = caculate_thisturnpossibleKeyword(allpossibleList,ASRkeywordList,allsubkey)
            mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
            if not allpossibleList: # or only filler
                if not inStr == 'nan':
                    unlistList.append('無語意詞-'+inStr)
                    accurancy.append('是') #ASR true
                else:
                    unlistList.append('#無法辨識')
                    accurancy.append('是') #ASR true
                #print('yes','no sub keyword','無偵測到關鍵字')
            else:
                notfiller = True
                # notfiller = False
                # for possible in allpossibleList:
                #     for item in possible.split(' '):
                #         if not item.replace('+','').replace('-','') in fillerList:
                #             notfiller = True
                #             break
                if notfiller:
                    accurancy.append('否')
                    unlistList.append('無語意詞-'+inStr)
                # else:
                #     accurancy.append('是(只有filler)')
                
        elif ASRresult == 'NoVoiceIn':
            subStrPossible.append('')
            matchKeywordList.append('')
            thisturnpossibleKeyword = caculate_thisturnpossibleKeyword(allpossibleList,ASRkeywordList,allsubkey)
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
            ASRkeywordList = [item[:-4].lower() for item in ASRresult.split('_')]
            # for item in ASRkeywordList:
            #     noSymbolitem = item.replace('+','').replace('-','') # check all symbol here!!
            #     if noSymbolitem in fillerList:
            #         ASRkeywordList.remove(item)
            sortallpossibleList = [sorted(item) for item in allpossibleList]
            if sorted(' '.join(ASRkeywordList)) in sortallpossibleList:
                ASRkeywordList = [item[:-4] for item in ASRresult.split('_')]
                accurancy.append('是')
                matchKeywordList.append(' '.join(ASRkeywordList))
                mostpossibleKeyword.append(';'.join(ASRkeywordList))
                subStrPossible.append('')
                unlistList.append('')
                if not humanListenAction == ASRAction:
                    #pass
                    print('check!! Not same Action')
                    #print(allpossibleList,inStr)
                #print('yes',allpossibleList,ASRkeywordList)
            else:
                thisturnpossibleKeyword = caculate_thisturnpossibleKeyword(allpossibleList,ASRkeywordList,allsubkey)
                mostpossibleKeyword.append(thisturnpossibleKeyword.replace(' ',';'))
                # 2 choice 1
                matchKeywordList.append('')
                subMean = False
                for service in serviceList:
                    if service[0] in ASRserviceList:
                        accurancy.append('是(語意部分相同)')
                        unlistList.append('')
                        subStrPossible.append('')
                        subMean = True
                        break
                if subMean:
                    continue

                inStr = re.sub(r'(\(.+\))','',str(inStr))
                if not allpossibleList:
                    accurancy.append('不列入')
                    
                    if inStr == '':
                        unlistList.append('#無法辨識')
                    else:
                        for filler in fillerList:
                            inStr = inStr.replace(filler,'')
                        unlistList.append('無語意詞-'+inStr)
                    subStrPossible.append('')
                
                else:
                    subStrPossible.append('')
                    if humanListenAction == ASRAction:
                        #print('change') KPI!
                        accurancy.append('是(語意相同)')
                        unlistList.append('')
                    else:
                        #check humanListenAction is leaf node or not
                        """
                        C: 正確辨識語意詞集合、D: 錯誤刪減語意詞集合、I: 錯誤加入語意詞集合、S: 標準答案語意詞集合、R: 辨識結果語意詞集合
                        S = C+D humanListenAction_Nodes
                        R = C+I ASRAction_Nodes
                        """
                        #print(humanListenAction,ASRAction)
                        #print(inStr)
                        humanListenAction_Nodes = re.findall('[LB];([一-龥]+)',humanListenAction)
                        ASRAction_Nodes = re.findall('[LB];([一-龥]+)',ASRAction)
                        actionIntersection = list(set(humanListenAction_Nodes).intersection(set(ASRAction_Nodes)))
                        if '已為您連結至' in ASRAction: # |L(R)|=1 
                            if '已為您連結至' in humanListenAction:
                                if ASRAction_Nodes == actionIntersection:
                                    #print('what! 2.1.1 L(R) = L(S)')
                                    accurancy.append('是( |L(S)|=1,|L(R)|=1')
                                    unlistList.append('')
                                else:
                                    accurancy.append('否( |L(S)|=1,|L(R)|=1')
                                    unlistList.append('')
                            else: #2.2.1	If L(R) ⊄ L(S)，則應算N
                                if not set(actionIntersection) == set(ASRAction_Nodes) :
                                    #print('N!',actionIntersection)
                                    accurancy.append('否( |L(S)|>1,|L(R)|=1  L(R) ⊄ L(S)')
                                    unlistList.append('')
                                else:
                                    #print(ASRAction,humanListenAction)
                                    accurancy.append('是( |L(S)|>1,|L(R)|=1 使用者意圖不清')
                                    unlistList.append('')
                                
                        else:# |L(R)| > 1 
                            if '已為您連結至' in humanListenAction:
                                if set(ASRAction_Nodes) == set(actionIntersection):
                                    #print('what! 2.3.1 L(R) = L(S)')
                                    accurancy.append('是( |L(S)|=1,|L(R)|>1  L(S) ⊂ L(R)')
                                    unlistList.append('')
                                else:
                                    accurancy.append('否( |L(S)|=1,|L(R)|>1  L(S) ∩ L(R) = φ')
                                    unlistList.append('')
                                    #print('N |L(R)|>1,|L(S)|=1,L(S) ∩ L(R) = φ')
                            else:
                                if set(ASRAction_Nodes) == set(actionIntersection):
                                    #print('what! 2.3.1 L(R) = L(S)')
                                    accurancy.append('是( |L(S)|>1,|L(R)|>1')
                                    unlistList.append('')
                                elif set(actionIntersection) == set(ASRAction_Nodes) :
                                    accurancy.append('是( |L(S)|>1,|L(R)|>1 L(S) ⊂ L(R)')
                                    unlistList.append('')
                                else:
                                    if actionIntersection:
                                        accurancy.append('否( |L(S)|>1,|L(R)|>1 L(S) ∩ L(R) ≠ φ')
                                        unlistList.append('')
                                    else:
                                        accurancy.append('否( |L(S)|>1,|L(R)|>1 L(S) ∩ L(R) = φ')
                                        unlistList.append('')
        if len(accurancy) != len(subkeyword):
            print(inStr)
            sys.exit()

                           



                        # filler_no_s = thisturnpossibleKeyword.replace('+','').replace('-','')
                        # if  filler_no_s in fillerList:
                        #     accurancy.append('是(只有filler)')
                        #     unlistList.append('無語意詞-'+inStr.replace(filler_no_s,''))
                        #     continue

                        # if len(ASRkeywordList) >= len(thisturnpossibleKeyword.split(' ')):
                        #     intersection = list(set(ASRkeywordList).intersection(set(thisturnpossibleKeyword.split(' '))))
                        #     if not intersection:
                        #         accurancy.append('否')
                        #         unlistList.append('')
                        #         continue
                        #     if sorted(intersection) != sorted(thisturnpossibleKeyword.split(' ')):
                        #         accurancy.append('否(有關鍵字詞未辨識)')
                        #         unlistList.append('')
                        #         continue
                            

                        #     diffSets = set(ASRkeywordList) - set(thisturnpossibleKeyword.split(' '))
                        #     #print(diffSets)    
                        #     checkStr = str(inStr)[:]
                        #     for item in intersection:
                        #         checkStr = checkStr.replace(item,' ')
                        #         checkStr = checkStr.replace(item.replace('+','').replace('-',''),' ')
                        #     checkStrList = checkStr.split(' ')
                        #     for item in thisturnpossibleKeyword.split(' '):
                        #         if item in checkStrList:
                        #             checkStrList.remove(item)

                        #     # if not intersection:
                        #     #     for item in ASRkeywordList:
                        #     #         checkStr = checkStr.replace(item,' ')
                        #     #         checkStr = checkStr.replace(item.replace('+','').replace('-',''),' ')
                        #     #     checkStrList = checkStr.split(' ')
                        #     newcheckStrList = []
                        #     for item in checkStrList:
                        #         if item in fillerList or item == '':
                        #             pass
                        #         else:
                        #             newcheckStrList.append(item)
                                
                            
                        #     if newcheckStrList:
                        #         accurancy.append('不列入')
                        #         unlistList.append('無語意詞-'+','.join(newcheckStrList))
                        #     else:
                        #         accurancy.append('不列入')
                        #         unlistList.append('#無法辨識')
                        #     #print(re.findall('\S+',''.join(diffSets)),'intersec:',intersection)
                        # else:
                        #     accurancy.append('否')
                        #     unlistList.append('')

                

    #print(allpossibleList,ASRkeywordList)
    #print(accurancy)
    #print(subkeyword)    
    #print(len(accurancy),len(subkeyword),len(matchKeywordList),len(subStrPossible))
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
    #print(df.head())
    # inputString = '不鏽鋼保溫壺'
    # allpossibleList = getAllpossible(inputString,allsubkey)
    # print(allpossibleList)

    #get candidate subkeywords in loadKW2SKW_SRC
    

if __name__ =='__main__':
    main()