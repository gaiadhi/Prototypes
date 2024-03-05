import json
from collections import namedtuple

def holos_json_hook(fn):
    f = open(fn)

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    return namedtuple('X', data.keys())(*data.values())

def parseHolosJson(jsonfName):
    #holosObj = json.loads (jsonfName, object_hook=holos_json_hook)
    holosObj = holos_json_hook(jsonfName)
    print (f"Done for {holosObj.UserID}")

if __name__ == "__main__":

    parseHolosJson("./UIV4_2.json")