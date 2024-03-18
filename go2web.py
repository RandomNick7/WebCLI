import socket
import re
import argparse
import sys

httpPort = 80

def getURL(sock, url):
    sock.connect((url, httpPort))
    sock.send(bytes("GET / HTTP/1.1\r\nHost:"+url+"\r\nConnection: close\r\n\r\n", 'UTF-8'))
    response = b""
    chunk = " "
    while len(chunk):
        chunk = sock.recv(256)
        response += chunk
    
    sock.close()
    print(response.decode('UTF-8'))

def searchTerm(sock, term):
    print(term)
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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if(len(sys.argv) == 1):
        print("Pass some arguments first! -h or --help for possible ones")

    if argList.url:
        getURL(sock, argList.url)
    if argList.search:
        searchTerm(sock, argList.search)


if __name__ == "__main__":
    main()