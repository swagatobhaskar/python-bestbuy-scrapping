from pathlib import Path
import json
import os

# location containing all json files
PATH = 'C:/Users/bhask/PycharmProjects/selenium/bestbuy_json/'

# list every path in the directory
paths = os.listdir(PATH)

# initialise the list that will hold every json as list element
grandMasterList = []

jsonParseCount = 0

# loop through each path
for file in paths:
    # Only JSON fies need to be taken
    if file.endswith(".json"):
        # concatenate the path with the filename to form absolute path
        absFilePath = f"{PATH}{file}"
        # display which file is being parsed now
        print(f"Parsing file: {absFilePath}")

        # open the file with its absolute path
        with open(absFilePath, 'r') as f:
            jsonParseCount += 1
            # load the file contents as json
            data = json.load(f)
            # append the json data to the list
            grandMasterList.append(data)

print(json.dumps(grandMasterList, indent=1))
print(jsonParseCount)

# create a new json file to write the list
grandMasterJSON = "grandMasterJSONList.json"
savePath = Path(PATH, grandMasterJSON)
with open(savePath, 'w') as ff:
    json.dump(grandMasterList, ff, indent=4)
