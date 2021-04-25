#!/usr/bin/env python3

import xmlrpc.client
import sys
import requests
import concurrent.futures

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

def showMenu():
    print("Welcome to wiki-pathfinder!\n")
    print("1) Find out the link between two wikipedia pages")
    print("0) Exit program")

def initSearch():
    while True:
        start = input("Start page: ")
        end = input("Target page: ")
        startValid = proxy.validatePage(start)
        endValid = proxy.validatePage(end)

        if startValid == False:
            print("Start page is not a valid wikipedia page, try again..\n")
            continue
        elif endValid == False:
            print("End page is not a valid wikipedia page, try again..\n")
            continue
        else:
            print("Pages are valid, finding the path")
            result = proxy.findPath(start, end)
            print("Path discovered: " + result)
            return

if __name__ == "__main__":
    try:
        while(True):
            showMenu()
            choise = input("Choose: ")
            if choise == "1":
                initSearch()
            elif choise == "0":
                sys.exit(0)
            else:
                print("Incorrect input, try again...")

    # if fails
    except xmlrpc.client.Fault as error:
        print("""\nCall to user API failed with xml-rpc fault!
    reason {}""".format(
            error.faultString))

    except xmlrpc.client.ProtocolError as error:
        print("""\nA protocol error occurred
    URL: {}
    HTTP/HTTPS headers: {}
    Error code: {}
    Error message: {}""".format(
            error.url, error.headers, error.errcode, error.errmsg))

    except ConnectionError as error:
        print("\nConnection error. Is the server running? {}".format(error))
