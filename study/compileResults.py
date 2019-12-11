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

outFileName = input()
outFile = open(outFileName, 'w')
for result in results:
    print(result/numLines)
    outFile.write(str(result/numLines))
    outFile.write("\n")