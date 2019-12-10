inFile = open("outFile.txt", 'r')

results = [0,0,0,0,0,0,0,0]
numLines = 0
for line in inFile:
    result = line.strip().split()
    print(result)
    for i in range(len(results)):
        results[i]+=float(result[i])
        numLines+=1/8

print(results)
print(numLines)
for result in results:
    print(result/numLines)