home = r'C:\Users\pc\Desktop\data'
n, k = 3, 5

import json
import re
import random as rd
patp = r'person_[0-9]+_9_0'
patc = r'person_[0-9]+_10_0'
num = 0
posNum = 0
testNum = 0
testPos = 0

for _ in range(5):
		#print(_)
		for i in range(100):
				dir = home+'/d ('+str(i+1)+')'
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
								p = p.replace('_9_0', '_10_0')
								d = {c:0}
								if g.get(p):
										g[p].update(d)
								else:
										g[p] = d

				person = list(ans.keys())
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
				friend = []
				for day in range(n-1):
						for id in newPOS:
								if g.get(id):
										ls = g[id].keys()#ls = [a[0] for a in sorted(g[id].items(), key = lambda a: a[1], reverse=True)]
										for p in ls:
												if p not in test:
														friend.append(p)
						newTest = friend[:k]
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
								if ans[id]:
										newPOS.append(id)
										#print(day+2, id)
						test += newTest
						pos += newPOS
				testPos += len(pos)
				testNum += len(test)
print(num//5, posNum//5, posNum/num)
print(testNum//5, testPos//5, testPos/testNum)
