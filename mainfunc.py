# coding=utf-8
import os
bifPath = '/home/yd/infection/bayesian-belief-networks-master/bayesian/examples/bif'
home = '/home/yd/infection/d2_addtional'
import sys
sys.path.append(bifPath)
sys.path.append(home)

from math import log
def entropy(ps):
    h = 0
    for p in ps.values():
        if 1> p > 0:
            h += -p * log(p, 2)
    return h
def initGraph(a, path):
    num = 0

    from bif_parser import parse
    for f in os.listdir(path):
        if '.bif' in f:
            # print f[:-4]
            parse(path+'/'+f[:-4])
            num += 1

    g = []
    names = [a+'.infection' + str(i) + '_bn' for i in range(num)]
    for name in names:
        exec 'import ' + name
        g.append(eval(name + '.create_bbn()'))
    return g, num

def loadAnswer(file):
    import json
    f = open(file, 'r')
    ans = {}
    p = 0
    for item in json.loads(f.read()):
        # item['id'] = item['id'][:-4] + '9' + item['id'][-2:]
        ans[item['id']] = item['isPositive']
        if item['isPositive']: p+=1
    f.close()
    return ans, p

# 输出：概率的字典
# key:{事件1：p1，事件2：p2，事件3：p3……}
def query(g, **kwds):
    dict = g.query(**kwds)
    res = {}
    for k in dict:
        d = res.get(k[0], {})
        d[k[1]] = dict[k]
        res[k[0]] = d
    return res

# 筛出一些有用的概率
def queryWith(pat, g, **kwds):
    temp = query(g, **kwds)
    from re import match
    res = {}
    for key in temp:
        if match(pat, key):
            res[key] = dict(temp[key].items()+[('H', entropy(temp[key]))])
    return res

def probInfer(gs, evi, pat):
    prob = []
    assumeProb = []
    for i, g in enumerate(gs):
        #print i
        prob.append(eval("queryWith(pat, g" + evi[i] + ")"))
        temp = {}
        for a in prob[i].keys():
            if a in evi[i]:
                continue
            #print a
            d = {
                'true': eval('queryWith(pat, g, ' + a + ' = "true"' + evi[i] + ')'),
                'false': eval('queryWith(pat, g, ' + a + ' = "false"' + evi[i] + ')')
            }
            temp[a] = d
        assumeProb.append(temp)
    return prob, assumeProb

def calEff(prob, assumeProb, entropyTable, effects, test=None, idS=None):
    for i, g in enumerate(prob):
        if idS and idS in g:
            effects[i][idS] = 0
            entropyTable[idS]['now'] = 0

            for key in assumeProb[i][idS]['true']:
                if key in test: continue
                entropyTable[key]['now'] = entropyTable[key][idS]
            for id in g:
                if id in test: continue
                a = 0
                for key in assumeProb[i][id]['true']:
                    if key in test: continue
                    # H(Xi|X1~Xs+1) = H(Xi|X1~Xs)(1-(H(Xs+1)-H(Xi|Xs+1))/H(xi))
                    HxS1 = g[id]['true'] * assumeProb[i][id]['true'][key]['H'] + \
                           g[id]['false'] * assumeProb[i][id]['false'][key]['H']
                    entropyTable[key][id] = entropyTable[key]['now'] * (
                                1 - (prob[i][id]['H'] - HxS1) / prob[i][key]['H'])
                    a += entropyTable[key]['now'] - entropyTable[key][id]

                effects[i][id] = a

        elif not idS:
            for id in g:
                if id in test: continue
                a = 0
                for key in assumeProb[i][id]['true']:
                    if key in test: continue
                    entropyTable[key][id] = g[id]['true'] * assumeProb[i][id]['true'][key]['H']+ \
                                            g[id]['false'] * assumeProb[i][id]['false'][key]['H']
                    a += entropyTable[key]['now'] - entropyTable[key][id]
                effects[i][id] = a

    return effects, entropyTable

def validate(ans, test, res):
    #print test
    #print ans
    right = 0
    for a in res:
        #print a, ans.get(a)
        if ans.get(a):
            right += 1
    return right, len(test)

def recommend(gs, num, pat, n, k, ans, TTT, RRR, confirmedProb=None, recommendProb=None):
    def recommendByProb(rbp):
        for i, g in enumerate(prob):
            for id in g:
                if id not in res:
                    if confirmedProb and g[id]['true'] > confirmedProb:  # 推断确诊
                        res.add(id)
                        RRR.append(('confirmed', id))
                        evi[i] += ',' + str(id) + '=true'
                    elif recommendProb and g[id]['true'] > recommendProb:  # 推荐检测
                        rbp += 1
                        if rbp > k:
                            continue
                        test.add(id)
                        TTT.append(('recommend', id))
                        evi[i] += ',' + str(id) + '=' + ['"false"', '"true"'][ans[id]]
                        if ans[id]:
                            res.add(id)
                            RRR.append(('recommend', id))
        return rbp

    test = set()
    res = set()
    evi = ["" for _ in range(num)]

    for day in range(n):
        prob, assumeProb = probInfer(gs, evi, pat)
        rbp = 0
        if confirmedProb or recommendProb:
            rbp = recommendByProb(rbp)

        maxId = None
        effects = [{} for _ in range(num)]
        entropyTable = {}
        for group in prob:
            for id in group:
                entropyTable[id] = {'now': group[id]['H']}
        #print entropyTable
        for _ in range(k - rbp):
            effects, entropyTable = calEff(prob, assumeProb, entropyTable, effects, test, maxId)
            #print effects
            #print entropyTable
            max = -100
            maxId = None
            maxI = -1
            for i, eff in enumerate(effects):
                for key in eff:
                    if key in test:
                        continue
                    if eff[key] > max:
                        max = eff[key]
                        maxId = key
                        maxI = i
            if not maxId: continue

            test.add(maxId)
            TTT.append(maxId)
            # print maxId, probs[day][maxI]
            evi[maxI] += ',' + str(maxId) + '=' + ['"false"', '"true"'][ans[maxId]]
            if ans[maxId]:
                res.add(maxId)
                RRR.append(maxId)

        #print validate(ans, test, res)
        #print TTT
        #print RRR
    #print "evi", evi
    return test, res, evi

def mainFunc(pid, dir, testTimes = (3, 2)):
    open(dir + '/__init__.py', 'w').close()
    n, k = testTimes

    TTT = []
    RRR = []
    gs, num = initGraph(pid, dir)
    print pid + ' begins'
    ans, p = loadAnswer(dir + '/answer.json')
    AAA = (p, len(ans))

    pat = 'person_[0-9]+_10_[0-9]+'

    test, res, evi = recommend(gs, num, pat, n, k, ans, TTT, RRR, 0.9)

    VVV = validate(ans, test, res)
    '''
    aaa = []
    bbb = []
    for i, g in enumerate(gs):
        aaa.append(g.qq())
        bbb.append(eval('g.qq(' + evi[i][1:] + ')'))
        '''

    # print VVV, TTT, RRR
    with open(dir + '/out.txt', 'w+') as f:
        f.write('轮数x每轮人数：' + str(testTimes) + '\n')
        f.write('答案阳性、总人数：' + str(AAA) + '\n')
        f.write('阳性、总检测人数：' + str(VVV) + '\n')
        f.write('检测id（有序）：' + str(TTT) + '\n')
        f.write('检测阳性id（有序）：' + str(RRR) + '\n')
        '''
        print >> f, '\n前'
        for a in aaa:
            print >> f, a
        print >> f, '\n后'
        for b in bbb:
            print >> f, b
            '''
    print pid + ' is done'


'''
import threading

threads = []
for a in [a for a in os.listdir(home) if os.path.isdir(a)]:
    subdir = home + '/' + a
    t = threading.Thread(target=mainFunc, args=(a, subdir,))
    threads.append(t)

for t in threads:
    t.start()
'''

from multiprocessing import Pool
if __name__ == '__main__':

    p = Pool()
    for a in [a for a in os.listdir(home) if os.path.isdir(a)]:
        subdir = home + '/' + a
        #os.rename(home + '/' + a, home + '/data2_new' + a)
        p.apply_async(mainFunc, args=(a, subdir, (3, 5)))

    p.close()
    p.join()

