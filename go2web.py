import socket
import argparse
import sys
import os
import json
import ssl
from bs4 import BeautifulSoup
from bs4.element import NavigableString

httpPort = 80
httpsPort = 443
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

def highlightJSON(soup):
    for s in ["[","]"]:
        soup = soup.replace(s, (c['yellow']+ s +c['none']))
    for s in ["\"","'"]:
        soup = soup.replace(s, (c['green']+ s +c['none']))
    for s in ["{","}"]:
        soup = soup.replace(s, (c['red']+ s +c['none']))
    for s in [":"]:
        soup = soup.replace(s, (c['yellow']+ s +c['none']))
    return soup

def getHTML(url, cache):
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
    
    path = path.lstrip('/')

    if host+'/'+path in cache:
        html = cache[host+'/'+path]
        soup = BeautifulSoup(html, "html.parser")
        if soup.html != None:
            s = soup.html.extract()
            return s
        else:
            return soup
    else:
        if url[:5] == "https":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, httpsPort))
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)
        else:
            sock.connect((host, httpPort))

        sock.sendall(bytes("GET /"+path+" HTTP/1.1\r\nHost:"+host+"\r\nConnection: close\r\n\r\n", 'UTF-8'))
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
            if soup.html != None:
                s = soup.html.extract()
                cache[host+'/'+path] = str(s)
                return s
            else:
                cache[host+'/'+path] = str(soup)
                return soup
        else:
            if html.split(' ',2)[1][0] == "3":
                sock.close()
                html = html[html.find("Location:") + len("Location:"):]
                html = html[:html.find("\n")]
                return getHTML(html[1:]+path, cache)
            else:
                print("Error - Received status:", html.split('\n',1)[0].split(' ',1)[1])
                return None


def getURL(url, cache):
    soup = getHTML(url, cache)
    if soup != None:
        if soup.body != None:
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
        else:
            soup = str(soup).strip()
            if soup[-1] == '0':
                soup = soup[:-1]
            soup = highlightJSON(soup)
            print(soup)

def searchTerm(term, cache):
    query = ""
    for word in term:
        query += word + '+'
    url = "https://www.google.com/search?q=" + query[:-1]
    soup = getHTML(url, cache)
    googleClass = "DnJfK"

    # Find the search result links and sanitize them
    if soup != None:
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
    cache = {}
    path = os.path.dirname(os.path.realpath(sys.argv[0]))

    with open(path+"/cache.txt",'a+') as f:
        f.seek(0)
        try:
            cache = json.loads(f.read())
        except:
            pass
        f.close()

    if(len(sys.argv) == 1):
        print("Pass some arguments first! -h or --help for possible ones")

    if argList.url:
        getURL(argList.url[0], cache)
    if argList.search:
        searchTerm(argList.search, cache)
    
    with open(path+"/cache.txt",'w+') as f:
        f.write(json.dumps(cache))
        f.close()


if __name__ == "__main__":
    main()