import statistics as stats
import json

df = json.load(open('modelstreamlinerResults.json', 'r'))

#print("UNSTREAMLINED:{0}".format(stats.mean(map(lambda x : x['savileRowTime'],df[""]['instanceStatsMapping'].values()))))

for key in df:
    print("{0}:{1}".format(key, stats.mean(map(lambda x : x['savileRowTime'],df[key]['instanceStatsMapping'].values()))))


