home = '/home/yd/infection/d2'
import os

n, k = 3, 5
pos = 0
sum = 0
test = [0 for _ in range(n)]
testP = [0 for _ in range(n)]

for a in os.listdir(home):
    b = home + '/' + a
    a = home + '/' + a + '/out.txt'
    if os.path.exists(a):
        with open(a, 'r') as f:
            list = f.readlines()
            t = list[1][list[1].find('(')+1:-2]
            t = [int(s) for s in t.split(',')]
            pos += t[0]
            sum += t[1]

            t = list[4][list[4].find('[')+1:-2]
            pL = [s[1:-1] for s in t.split(', ')]
            t = list[3][list[3].find('[')+1:-2]
            tL = [s[1:-1] for s in t.split(', ')]
            if len(tL)<15: print a
            #else: print 111, a

            for i in range(n):
                for p in tL[i*k : (i+1)*k]:
                    test[i] += 1
                    if p in pL:
                        testP[i] += 1

        # break
    elif os.path.exists(b):
    	print b
with open('statistic.txt', 'w+') as f:
    for i in range(1, n):
        test[i] += test[i-1]
        testP[i] += testP[i-1]
    print >>f, " \t" + str(pos) + '\t\t' + str(sum) + '\t' + str(pos/float(sum))
    for i in range(n):
        print >>f, str(i+1) + '\t' + str(testP[i]) + '\t\t' + str(test[i]) + '\t' + str(testP[i]/float(test[i]))
