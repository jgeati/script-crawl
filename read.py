import json
import ast

with open('C:/Users/Owner/crawls/reader0.json', 'r', encoding='utf-8') as f:
   lines = f.readlines()

output = {}

for s in lines:
    print(s)
    break
    # split_line = s.split(",")
    # first = split_line[0].strip()
    # print(first)
    # output[first] = {}
    # output[first][first] = split_line[1].strip()
    # pairs = []
    # for i in range(0, len(split_line[2:]), 2):
    #     pairs.append(split_line[2:][i:i+2])
    #
    # for pair in pairs:
    #     try:
    #         day = pair[0].strip()
    #         output[first].setdefault(day, []).append(pair[1].strip())
    #     except:
    #         day = pair[0].strip()
    #         output[first].setdefault(day, []).append('nope')
    #
    # print(output)
    # for key in output.keys():
    #     print(key)
