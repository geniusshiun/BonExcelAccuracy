
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
            subkeyword = line.lower()
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
        
    allcandidateSubdict = sorted(allcandidateSubdict.items(), key=lambda kv: kv[1],reverse=True)
    allcandidateSub = [allcandidateSubdict[i][0] for i in range(len(allcandidateSubdict))]
    allcandidateSub = [item for item in allcandidateSub if len(item) > 1]
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
                if item[1] in symboleItem:
                    newgroup.append(symboleItem[item[1]])
                else:
                    newgroup.append(item[1])
            if newgroup:
                allpossible.append(' '.join(newgroup))
    return (list(set(allpossible)))
def main():
    
    #keyworddict,allsubkey,symboleItem = loadKW2SKW('sw2a_1206v1.xlsx.csv-step3.words')
    keyworddict,allsubkey,symboleItem = loadSW2IDX('sw2idx_1206v1')
    #print(symboleItem)
    #if 'card' in allsubkey:
    #    print('inin')
    #print(keyworddict)
    #print(getAllpossible('我要繳電話費',allsubkey,symboleItem))
    #sys.exit()
    #load excel
    df = pd.read_excel('語音互動詢答1217_1223(iBonPWSTD_stage3_20181206_NG)_1228YH.xlsx')#,header=None
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
    for i in range(len(df)):
        inStr = df.iloc[i]['標記逐字稿']
        ASRresult = df.iloc[i]['ASR辨識結果']
        humanListenAction = df.iloc[i]['逐字稿斷詞語意結果']
        ASRAction = df.iloc[i]['ASR辨識語意結果']
        allpossibleList = getAllpossible(inStr,allsubkey,symboleItem)
        
        subkeyword.append(','.join(allpossibleList))
        serviceList = re.findall('已為您連結至(.+)的(.+)服務',humanListenAction)
        ASRserviceList = []
        if '」還是「' in ASRAction:
            ASRserviceList = re.findall('「(.+)」',ASRAction)
            ASRserviceList = ASRserviceList[0].split('」還是「')
            #print(ASRserviceList)
        if ASRresult == '無偵測到關鍵字':
            subStrPossible.append('')
            matchKeywordList.append('')
            if not allpossibleList:
                accurancy.append('不列入') #ASR true
                #print('yes','no sub keyword','無偵測到關鍵字')
            else:
                accurancy.append('否')
                #print('no',allpossibleList,'vs 無偵測到關鍵字')
        elif ASRresult == 'NoVoiceIn':
            subStrPossible.append('')
            matchKeywordList.append('')
            if str(inStr) == 'nan':
                accurancy.append('不列入')
                #print('yes',ASRresult)
                pass
            else: #ASR False
                if not allpossibleList:
                    accurancy.append('否')
                else:
                    accurancy.append('否')
                    print('check!!')
        else:
            #for y in list(set(symbolList)):
            #    ASRkeywordList = [item[:-4].replace(y,'') for item in ASRresult.split('_')]
            ASRkeywordList = [item[:-4] for item in ASRresult.split('_')]
            
            if ' '.join(ASRkeywordList) in allpossibleList:
                accurancy.append('是')
                matchKeywordList.append(' '.join(ASRkeywordList))
                subStrPossible.append('')
                if not humanListenAction == ASRAction:
                    pass
                    #print('check!! Not same Action')
                    #print(allpossibleList,inStr)
                #print('yes',allpossibleList,ASRkeywordList)
            else:
                matchKeywordList.append('')
                subMean = False
                for service in serviceList:
                    if service[0] in ASRserviceList:
                        accurancy.append('是(語意部分相同)')
                        subStrPossible.append('')
                        subMean = True
                        break
                if subMean:
                    continue

                #computer left words in allsubkey?
                checkStr = str(inStr)[:]
                for asrkey in ASRkeywordList:
                    checkStr = checkStr.replace(asrkey.lower(),' ')
                
                thissubPossible = []
                for subStr in checkStr.split(' '):
                    if subStr == '':
                        continue
                    subPossible = getAllpossible(subStr,allsubkey,symboleItem)
                    if len(subPossible) > 0:
                        thissubPossible.extend(subPossible)
                        subPossible = []

                if not allpossibleList:
                    accurancy.append('不列入')
                    subStrPossible.append('')
                elif len(thissubPossible) > 0:
                    subStrPossible.append(thissubPossible)
                    accurancy.append('否(有關鍵詞未辨識)')
                
                    

                # if not checkStr in allsubkey:
                #     accurancy.append('不列入(有未建立詞)')
                #     subStrPossible.append('')
                
                else:
                    subStrPossible.append('')
                    if humanListenAction == ASRAction:
                        #print('change') KPI!
                        accurancy.append('是(語意相同)')
                    else:
                        accurancy.append('否')
                #print('no',allpossibleList,ASRkeywordList)

            #print(allpossibleList,ASRkeywordList)
    #print(accurancy)
    #print(subkeyword)    
    #print(len(accurancy),len(subkeyword),len(matchKeywordList),len(subStrPossible))
    df['accuracy'] = accurancy
    df['subkeyword'] = subkeyword
    df['matchKeyword'] = matchKeywordList
    df['subStrPossible'] = subStrPossible
    df1 = df[['標記逐字稿','ASR辨識結果','subkeyword','逐字稿斷詞結果','matchKeyword','accuracy','語音辨識是否正確']]
    
    writer = pd.ExcelWriter('1217_idx.xlsx',engine='xlsxwriter')
    df1.to_excel(writer,'Sheet1')

    writer.save()
    #print(df.head())
    # inputString = '不鏽鋼保溫壺'
    # allpossibleList = getAllpossible(inputString,allsubkey)
    # print(allpossibleList)

    #get candidate subkeywords in loadKW2SKW_SRC
    

if __name__ =='__main__':
    main()