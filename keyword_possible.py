import argparse
import re
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
def loadfile(filepath):
    inputList = []
    with open(filepath,'r',encoding='utf8') as f:
        for line in f.readlines():
            inputList.append(line.strip())
    return inputList
def main():
    
    parser = argparse.ArgumentParser("Script for possible generate")
    parser.add_argument("--filepath", '-t', type=str, required=True,help='filepath')
    parser.add_argument("--idxpath", '-idx', type=str, required=True,help='idxpath')
    parser.add_argument("--filler", '-f', default = '',type=str,help='filler path')
    args = parser.parse_args()
    keyworddict,allsubkey,symboleItem = loadSW2IDX(args.idxpath)#'sw2idx_0119v6'
    #allsubkey.extend(['臺灣','臺鐵','臺北','臺中','臺南','臺東','台灣','台鐵','台北','台中','台南','台東'])
    allsubkey = list(set(allsubkey))
    fillerList = []
    if not args.filler == '':
        fillerList = loadfile(args.filler)
        allsubkey.extend(fillerList)
    filepath = args.filepath#'allhumankey'
    
    result = ''
    lineCnt = 0
    fillercount = {}
    # fillertag = False
    for inStr in loadfile(filepath):
        
        allpossibleList = getAllpossible(inStr,allsubkey,symboleItem)
        # print(allpossibleList)
        newallpossibleList = []
        for items in allpossibleList:
            tmpitem = []
            for item in items.split(' '):
                if item in fillerList:
                    item = '*'+item+'*'
                    # fillertag = True
                tmpitem.append(item)
            newallpossibleList.append(' '.join(tmpitem))
        # print(newallpossibleList)
        

        for items in newallpossibleList:
            lineCnt+=1
            inStrList = []
            inStr = inStr.lower()
            newStr = inStr
            #print('items.split(' ')',items.split(' '))
            for item in items.split(' '):
                if item in inStr:
                    inStrList.append(item)
                elif item.replace('+','').replace('-','') in inStr:
                    inStrList.append(item.replace('+','').replace('-',''))
                elif '*' in item:
                    inStrList.append(item.replace('*',''))
            #print(inStrList)
            for item in inStrList:
                start = [m.start() for m in re.finditer(item,inStr)]
                end = [m.end() for m in re.finditer(item,inStr)]
                for s, e in zip(start,end):
                    if s == 0:
                        newStr = newStr.replace(item, item+' ')
                    elif e == len(inStr):
                        newStr = newStr.replace(item, ' '+item)
                    else:
                        newStr = newStr.replace(item, ' '+item+' ')
                #start, end = [m.start(), m.end() for m in re.finditer(item,inStr)][0]
                #print(start,end)
            newStr = ' '.join([item for item in newStr.split(' ') if not item == ''])
            resultList = []
            #print(newStr.split(' '))
            for item in newStr.split(' '):
                if item in symboleItem:
                    resultList.append(symboleItem[item])
                elif item in fillerList:
                    resultList.append('*'+item+'*')
                else:
                    resultList.append(item)
            try:
                for item in resultList:
                    if not item in allsubkey:
                        if item.upper() in allsubkey:
                            continue
                        if not item in fillercount:
                            fillercount[item] = 1
                        else:
                            fillercount[item] += 1
                result+=' '.join(resultList)+'\t'+items.replace(' ',',')+'\n'
                #print(result)
            except:
                print('|'.join(inStrList),inStr,items)
            # if fillertag:
            #     sys.exit(0)
            #result+=str(lineCnt)+' '+inStr+' => '+items.replace(' ',',')+'\n'
        
    #print(result)
                
    #print(fillercount)
    report = []
    sorted_fillercount = sorted(fillercount.items(), key=lambda x: x[1],reverse = True)
    for item in sorted_fillercount:
        if item[1] >= 10 and len(item[0]) > 1 and len(re.findall(r'[一-龥]',item[0])) > 1:
            parentheses = re.findall(r'(\(.+\))',item[0])
            if parentheses:
                newitem = item[0].replace(parentheses[0],'')
                if len(newitem) > 1:
                    report.append((newitem,item[1]))
            else:
                report.append(item)
    fillers = []
    for item in report:
        fillers.append(item[0])
    fillers = list(set(fillers))
    if not fillerList:
        with open(args.idxpath+'filler','w',encoding='utf8') as f:
            for item in fillers:
                f.write(item+'\n')
        with open(args.idxpath+'fillerWithStarForSyllable','w',encoding='utf8') as f:
            for item in fillers:
                f.write('*'+item+'*'+'\n')
        with open(args.idxpath+'fillerWithStar','w',encoding='utf8') as f:
            for item in fillers:
                f.write('*'+item+'*'+'\t1\t'+'*'+item+'*'+'\n')

    # with open('Filler.txt','r',encoding='utf8') as f:
    #     for line in f.readlines():
    #         line = line.strip().replace(' ','')
    #         cnt = 0
    #         for item in sorted_fillercount:
    #             if line in item[0]:
    #                 cnt+=item[1]
    #         print(line,cnt)
            
    #print(dict(list(sorted_fillercount.items())[0:20]))
    with open('allhumankeyAllpossible_TEMP_0307','w',encoding = 'utf8') as f:
        f.write(result)
if __name__ =='__main__':
    main()
    