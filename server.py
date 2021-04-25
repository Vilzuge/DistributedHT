#!/usr/bin/env python3

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import Fault
from socketserver import ThreadingMixIn

import requests
import concurrent.futures

S = requests.Session()
URL = "https://fi.wikipedia.org/w/api.php"

def validatePage(title):
    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "links",
        "pllimit": "max"
    }
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    PAGES = DATA["query"]["pages"]
    if "-1" in PAGES:
        print("Page is invalid")
        return False
    else:
        print("Page is valid...")
        return True
    

def deleteDuplicates(theList):

    #https://stackoverflow.com/questions/42764335/python-find-duplicates-in-the-first-col-of-a-2d-list-and-remove-one-of-them-base
    #https://stackoverflow.com/questions/7436267/python-transform-a-dictionary-into-a-list-of-lists
    output_lst = dict()
    for n, v in theList:
        if n in output_lst:
            output_lst[n] = max(output_lst[n], v)
        else:
            output_lst[n] = v    # The question is, what is the complexity of this operation
    returnList = list(map(list, output_lst.items()))
    return returnList

def getPageLinks(pageTitle, currentPath):
    allLinks = []
    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": pageTitle,
        "prop": "links",
        "pllimit": "max"
    }
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    PAGES = DATA["query"]["pages"]
    if "-1" not in PAGES:   #basically if we found a wikipedia page or not
        for k, v in PAGES.items():
            try:
                for l in v["links"]:
                    allLinks.append([ l["title"], currentPath + " >> " + l["title"]])
                    #print([ l["title"], currentPath + " >> " + l["title"] ])
            except KeyError:
                print("Failed to get links")

    while 'continue' in DATA:   #getting additional pages with plcontinue
        PARAMS = {
            "action": "query",
            "format": "json",
            "titles": pageTitle,
            "prop": "links",
            "pllimit": "max",
            "plcontinue": DATA["continue"]["plcontinue"]
        }
        R = S.get(URL, params=PARAMS)
        DATA = R.json()
        PAGES = DATA["query"]["pages"]  
        if "-1" not in PAGES:
            for k, v in PAGES.items():
                try:
                    for l in v["links"]:
                        allLinks.append([ l["title"], currentPath + " >> "+ l["title"]])
                        #print([ l["title"], currentPath + " >> " + l["title"] ])
                except KeyError:
                    print("Failed to get links")

    print("Found " + str(len(allLinks)) + " links, returning them back")
    return allLinks

def runParallel(inputArray, endTitle):
    newArray = []
    for i in range(0, len(inputArray), 10):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            try:
                args = ((inputArray[k][0], inputArray[k][1]) for k in range(i,i+9))
                for out in executor.map(lambda p: getPageLinks(*p), args):
                    newArray = newArray + out
            except:
                print("Error occurred in indexing")
            newArray = deleteDuplicates(newArray)
            print(str(len(newArray)) + " is the size now..")

        print("Finished a cycle")
        titleList = [element[0] for element in newArray]
        for i in range(len(titleList)):
            if titleList[i].upper() == endTitle.upper():
                print(newArray[i][1])
                result = newArray[i][1]
                return result, "found"
    newArray = deleteDuplicates(newArray)
    return newArray, "unfound"


def findPath(startTitle, endTitle):

    currentPath = startTitle
    startArray = getPageLinks(startTitle, currentPath)

    #if only one link is returned, get page links from the single page only
    while len(startArray) == 1:
        startArray = getPageLinks(startArray[0][0], startArray[0][1])

    # while the result has not been found
    while(True):
        # run a function in parallel that finds links of a page (10 simultaneously)
        result, didFind = runParallel(startArray, endTitle)
        if didFind == "found":
            return result
        else:
            #move on to next level
            startArray = result


class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

#https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1
def run_server(host="localhost", port=8000):
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)
    #server.register_function(deleteDuplicates)
    #server.register_function(getPageLinks)
    #server.register_function(runParallel)
    server.register_function(validatePage)
    server.register_function(findPath)

    print("Server thread started. Testing server ...")
    print('listening on {} port {}'.format(host, port))

    server.serve_forever()

if __name__ == "__main__":
    run_server()