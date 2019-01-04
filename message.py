
import pandas as pd
import collections
import re
import sys

def main():
    ouputfilename = 'message1211'
    df = pd.read_excel('語音互動詢答1211_1216(iBonPWSTD_stage3_20181206_NG)_1221YH(安源_連續語意回應比較結果).xlsx')#,header=None
    mainIDList = df.drop_duplicates(subset=['主明細ID'],keep='first')['主明細ID'].values
    index = 0
    finalmessage = []
    AandBformatIDs = df[df['ASR連續語意回應結果(DM 2.4版)'].str.contains(r'[一-龥「」]+ 與 [一-龥「」]+')]['主明細ID'].values#.drop_duplicates(subset=['主明細ID'],keep='first')['主明細ID'].values
    
    for mainID in mainIDList:
        message = []
        ASRresultList = list(df[df['主明細ID'] == mainID]['ASR辨識結果'].values)
        DM24 = list(df[df['主明細ID'] == mainID]['ASR連續語意回應結果(DM 2.4版)'].values)
        allKeyword = {}
        for item in ASRresultList:
            for each in item.split('_'):
                keyword = each
                if keyword in ['無偵測到關鍵字','NoVoiceIn']: # remove this two possible, discussable
                    continue
                if '[' in each and ']' in each:
                    keyword = each[:-4]
                if not keyword in allKeyword:
                    allKeyword[keyword] = 1
                else:
                    allKeyword[keyword] += 1
        sortAllK = sorted(allKeyword.items(), key = lambda k:k[1],reverse=True)
        if sortAllK and sortAllK[0][1] > 1:
            #DM24 = list(df[df['主明細ID'] == mainID]['ASR連續語意回應結果(DM 2.4版)'].values)
            newDM24 = []
            for item in DM24:
                if item == 'SemanticWords_Not_Found':
                    newDM24.append(item)
                else:
                    newDM24.append(re.findall('([ 一-龥「」?？，、A-Za-z0-9]+)@',item)[0])  
            DM21 = list(df[df['主明細ID'] == mainID]['ASR連續語意回應結果(DM 2.1版)'].values)
            newDM21 = []
            for item in DM21:
                if item == 'SemanticWords_Not_Found':
                    newDM21.append(item)
                else:
                    newDM21.append(re.findall('([ 一-龥「」?？，、A-Za-z0-9]+)@',item)[0])   
            #DM21 = [re.findall('([一-龥「」?？，、A-Za-z0-9]+)@',item)[0] for item in DM21 if not item == 'SemanticWords_Not_Found']
            message.append(mainID)
            for i in range(len(ASRresultList)):
                message.append('A:'+ASRresultList[i])
                message.append('DM 2.4版:'+newDM24[i])
                message.append('DM 2.1版:'+newDM21[i])
            message.append('='*30+'\n')
            # print(ASRresultList)
            # print(mainID)
            # print(sortAllK)
            index+=1
        finalmessage.append(message)
        # if index > 10:
        #     break
    with open(ouputfilename,'w',encoding='utf8') as f:
        for message in finalmessage:
            f.write('\n'.join(message))
    
    finalmessage = []
    # ===========================================
    # another file DM2.4版(AH欄位) 有 * 與 * 的，輸出該次所有對話 。
    existmainID = []
    for mID in AandBformatIDs:
        if not mID in existmainID:
            existmainID.append(mID)
        else:
            continue
        message = []
        ASRresultList = list(df[df['主明細ID'] == mID]['ASR辨識結果'].values)
        DM24 = list(df[df['主明細ID'] == mID]['ASR連續語意回應結果(DM 2.4版)'].values)
        
        newDM24 = []
        for item in DM24:
            if item == 'SemanticWords_Not_Found':
                newDM24.append(item)
            else:
                newDM24.append(re.findall('([ 一-龥「」?？，、A-Za-z0-9]+)@',item)[0])  
        message.append(mID)
        for i in range(len(ASRresultList)):
            message.append('A:'+ASRresultList[i])
            message.append('DM 2.4版:'+newDM24[i])
        message.append('='*30+'\n')
        finalmessage.append(message)
    with open(ouputfilename+'AandB','w',encoding='utf8') as f:
        for message in finalmessage:
            f.write('\n'.join(message))
    # for i in range(len(df)):
    #     inStr = df.iloc[i]['標記逐字稿']
    #     ASRresult = df.iloc[i]['ASR辨識結果']#1226NG ASR結果
    #     humanListenAction = df.iloc[i]['逐字稿斷詞語意結果']
    #     ASRAction = df.iloc[i]['ASR辨識語意結果']
if __name__ == '__main__':
    main()