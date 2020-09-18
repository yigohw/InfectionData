home = r'C:\Users\admin\Desktop\data'
n, k = 10, 6
nnn = 10
import json
import re
import random as rd
patp = r'person_[0-9]+_[0-9]+_0'
patc = r'person_[0-9]+_[0-9]+_0'
num = 0
posNum = 0
testList = [0 for _ in range(n)]
testPosList = [0 for _ in range(n)]

for _ in range(nnn):

        for i in range(30):
                dir = home+'/'+str(i)
                #print(i)
                ans = {}
                with open(dir+'/answer.json', 'r') as f:
                        dic = json.load(f)
                        for d in dic:
                                ans[d['id']] = d['isPositive']
                num += len(ans)
                for a in ans.keys():
                        if ans[a] == 1:
                                posNum += 1

                with open(dir+'/sourceData.json', 'r') as f:
                        edges = json.load(f)['edges']
                g = {}
                for e in edges:
                        #print(e)
                        p = e['parent']
                        c = e['child']
                        if re.match(patp, p) and re.match(patc, c):
                                p = re.sub('_[0-9]+_0', '_23_0', p)
                                d = {c:0}
                                if g.get(p):
                                        g[p].update(d)
                                else:
                                        g[p] = d

                person = list(ans.keys())
                #print(g)
                test = []
                pos = []
                newTest = []
                newPOS = []
                for i in range(k):
                        id = rd.choice(person)
                        person.remove(id)
                        newTest.append(id)
                for id in newTest:
                        if ans[id]:
                                newPOS.append(id)
                                #print(1, id)
                test += newTest
                pos += newPOS
                friend = [];testPosList[0] += len(pos);testList[0] += len(test)
                for day in range(n-1):
                        for id in newPOS:
                                if g.get(id):
                                        ls = g[id].keys()
                                        #print(id)#ls = [a[0] for a in sorted(g[id].items(), key = lambda a: a[1], reverse=True)]
                                        for p in ls:
                                                p = re.sub('_[0-9]+_0', '_23_0', p)
                                                if p not in test and p not in friend:
                                                        friend.append(p)
                        newTest = friend[:k]
                        #print("friend", friend)
                        if len(friend)>k:
                                newTest = friend[:k]
                                friend = friend[k:]
                        else:
                                for i in range(k-len(friend)):
                                        id = rd.choice(person)
                                        person.remove(id)
                                        newTest.append(id)
                                friend = []
                        newPOS = []
                        for id in newTest:
                                #id = re.sub('_[0-9]+_0', '_23_0', id)
                                #print(id)
                                if ans[id]:
                                        newPOS.append(id)
                                        #print(day+2, id)
                        test += newTest
                        pos += newPOS;testPosList[day+1] += len(pos);testList[day+1] += len(test)#;print(test);print(pos)
print((num//nnn, posNum//nnn), list(zip([j//nnn for j in testList], [j//nnn for j in testPosList])))