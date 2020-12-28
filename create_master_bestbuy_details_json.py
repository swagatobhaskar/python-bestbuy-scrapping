from pathlib import Path
import json
import os

# location containing all json files
PATH = 'C:/Users/<username>/<path>/<to>/<json files>/'

# list every path in the directory
paths = os.listdir(PATH)

# initialise the list that will hold every json as list element
masterList = []

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
            # load the file contents as json
            data = json.load(f)
            # append the json data to the list
            masterList.append(data)

# create a new file to write the list as json
masterJSONFile = "masterJSONList.json"
savePath = Path(PATH, masterJSONFile)

with open(savePath, 'w') as master_file:
    json.dump(masterList, master_file, indent=4)
