import json
import discord

coordinates = json.load(open('coordinates.json'))

nations = ['niue', 'frenchpolynesia', 'fiji', 'tuvalu', 'tokelau', 'cookislands', 'pitcairnislands', 'samoa', 'tonga', 'wallisandfutuna', 'vanuatu', 'kiribati']
triosets = ['island', 'sea', 'ship', 'ocean']

#Set 1: island, sea
#Set 2: ship, ocean
#returns: embedVar
def visit_island(content):
  try:
    inputData = content.split('-')
    print(inputData)
    if len(inputData) != 3 or inputData[0] != '$navigate' or inputData[1] not in triosets or inputData[2] not in nations:
      raise ValueError
  except:
    return "Invalid input"

  setName = inputData[1]
  set = "1" if inputData[1] in ('island', 'sea') else "2"
  nation = inputData[2]
  
  outputData = coordinates[set][nation]

  return outputData
