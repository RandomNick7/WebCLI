import socket
import re
import argparse
import sys

def getURL():
    pass

def searchTerm():
    pass

def argParseSetup():
    argParser = argparse.ArgumentParser(
        prog='go2web',
        description='CLI app to make HTTP requests to specified sites',
    )
    args = argParser.add_mutually_exclusive_group()
    args.add_argument('-u', '--url', help='make an HTTP request to the specified URL and print the response')
    args.add_argument('-s', '--search', help='make an HTTP request to search the term using your favorite search engine and print top 10 results')
    return argParser.parse_args()

def main():
    argList = argParseSetup()

    if(len(sys.argv) == 1):
        print("Pass some arguments first! -h or --help for possible ones")

    if argList.url:
        getURL(argList.url)
    if argList.search:
        searchTerm(argList.search)


if __name__ == "__main__":
    main()