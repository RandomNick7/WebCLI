import socket
import re
import argparse
import sys
import os
import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString

httpPort = 80
os.system("")  # Enables ANSI escape characters in terminal

c = {
    "black": "\033[90m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "mangenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "none": "\033[0m"
}

def getHTML(sock, url, cache):
    host = ""
    path = ""
    if url[:4] == "http":
        host = url.split('/',3)[2]
        try:
            path = url.split('/',3)[3]
        except:
            pass
    else:
        host = url.split('/',1)[0]
        try:
            path = url.split('/',1)[1]
        except:
            pass
    
    sock.connect((host, httpPort))
    sock.send(bytes("GET /"+path+" HTTP/1.1\r\nHost:"+host+"\r\nConnection: close\r\n\r\n", 'UTF-8'))
    response = b""
    chunk = " "
    while len(chunk):
        chunk = sock.recv(256)
        response += chunk
    
    sock.close()
    html = ""
    try:
        html = response.decode('UTF-8')
    except:
        html = response.decode('latin-1')
    
    if html.split(' ',2)[1] == "200":
        soup = BeautifulSoup(html, "html.parser")
        # Remove invisible stuff from the soup, return just the body
        for data in soup(['style','script','head']):
            data.decompose()
        return soup.html.extract()
    else:
        print("Error - Received status:", html.split('\n',1)[0].split(' ',1)[1])
        return None


def getURL(sock, url, cache):
    soup = getHTML(sock, url, cache)
    if soup != None:
        for elem in soup.body.descendants:
            if(elem.name != None):
                if(elem.string != None):
                    for e in elem.contents:
                        if(type(e) == NavigableString):
                            print(c['white'], elem.string.strip(), c['none'])
                if elem.has_attr('href'):
                    print(c['cyan'], elem['href'], c['none'])
                if elem.has_attr('src'):
                    print(c['blue'], elem['src'], c['none'])

def searchTerm(sock, term, cache):
    query = ""
    for word in term:
        query += word + '+'
    url = "https://www.google.com/search?q=" + query[:-1]
    soup = getHTML(sock, url, cache)
    googleClass = "DnJfK"

    # Find the search result links and sanitize them
    for item in soup.find_all("div", class_=googleClass):
        print(c['green'], item.find('h3').getText(), c['none'])
        addr = item.parent['href']
        # Google's prefixes for links
        addr_start = addr.find("?q=")
        if(addr_start != -1):
            addr = addr[addr_start + len("?q="):]
        # Google's suffix always starts with &
        addr_end = addr.find('&')
        if(addr_end != -1):
            addr = addr[:addr_end]
        print(c['cyan'], addr, c['none'])

def argParseSetup():
    argParser = argparse.ArgumentParser(
        prog='go2web',
        description='CLI app to make HTTP requests to specified sites',
    )
    args = argParser.add_mutually_exclusive_group()
    args.add_argument('-u', '--url', nargs=1, help='make an HTTP request to the specified URL and print the response')
    args.add_argument('-s', '--search', nargs='+', help='make an HTTP request to search the term using your favorite search engine and print top 10 results')
    return argParser.parse_args()

def main():
    argList = argParseSetup()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cache = {}

    if(len(sys.argv) == 1):
        print("Pass some arguments first! -h or --help for possible ones")

    if argList.url:
        getURL(sock, argList.url[0], cache)
    if argList.search:
        searchTerm(sock, argList.search, cache)


if __name__ == "__main__":
    main()