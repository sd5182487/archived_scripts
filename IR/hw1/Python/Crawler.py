#cs6200 summer2 hw1 - Q2 crawler
#author Hao.H
#Documents
'''

    This crawler uses BFS algrithm which is pretty strong in parsing inside the domain and but at same time, it will meet more dup links this way.
    That will cost more memory to process.So as this volunerability it is obvious that this crwaler cant be used in production
    (slow and cost tons of memory/storage,as well as hated by people when you crawl their sites).
    Condsider using multi thread or random crawl will improve the performance.
    And I finally find how to comment mutilple lines..Viva google..
    
'''
from HTMLParser import HTMLParser
import urlparse
import urllib
import time
import robotparser
import sys
reload(sys)
sys.setdefaultencoding("utf-8")  #compatiable with pages

#wish list : a parser to read urls
#HTMLParser()

class Search_NEU(HTMLParser):
    def __init__(spider):
        HTMLParser.__init__(spider)
        #adding function to deal with redirect links
        spider.new_target = []
        #spider.isredirect = False   no need to deal with it as I use standard lib
        spider.cur_url = None
    
    def res_temp(spider):
        status.res[spider.cur_url] = status.outgoing
        status.outgoing = []
    
    def this_seed(spider, html_response):
        spider.feed(html_response.read())
        for link in spider.new_target:
            new_url = spider.canonlize_url(link)
            if new_url:
                status.process_url(link)
            continue
        #init
        spider.res_temp()
        spider.new_target = []
    
    
    
    def canonlize_url(spider, raw_url):
        if not str(raw_url).startswith('http'):
            if str(raw_url).startswith("mailto"):
                return None
            raw_url = urlparse.urljoin(spider.cur_url, raw_url)
        response_url = str(urlparse.urldefrag(raw_url)[0]).replace('/../', '/')
        if ' ' in response_url:
            return None
        if response_url.endswith('/'):
            response_url = response_url[:-1]
        return response_url
    
    #reload tag dealer
    #? how about redirect urls?
    #example:  http://www.northeastern.edu/findfacultystaff
    #-->  https://prod-web.neu.edu/wasapp/employeelookup/public/main.action
    def handle_starttag(spider, tag, attrs):
        if tag == 'a':
            for (name, value) in attrs:
                if name == 'href':
                    spider.new_target.append(value)    #normal html url


#and a spider controller
#SpiderController
class SpiderController():
    #struct for spider
    def __init__(spider):
        spider.frontier = []
        spider.visited = []
        spider.allowed_type = ['html', 'pdf']
        spider.allowed_domain = ['neu.edu', 'northeastern.edu']
        #spider.header = {'User-Agent': 'Mozilla/5.0'}
        spider.res = {}
        spider.count = 0
        spider.last_query = None
        spider.denied = []
        spider.outgoing = []
        spider.robots = {}
        spider.robots_list = None
    
    #first run takes around 50mins..holy.. let's try wait for less sometimes
    def wait(spider):
        if spider.last_query:
            time.sleep(5 - (time.time() - spider.last_query))
            spider.last_query = time.time()
        else:
            spider.last_query = time.time()
    
    def valid_url(spider, dest_url):
        url_parse = urlparse.urlparse(dest_url)
        host = url_parse.hostname
        if host not in spider.robots:
            robots_url = urlparse.urljoin(dest_url, "/robots.txt")
            try:
                spider.wait()
                #import robot.txt
                robots_list = urlopener.open(robots_url)
            #thanks to yilin,adding this to avoid some IO/permission issues
            except IOError:
                return False
            else:
                spider.robots[host] = robots_list
        else:
            robots_list = spider.robots[host]
        
        if robots_list:
            read_robots = robotparser.RobotFileParser()
            #encountered some socket err 054,adding try just in case
            try:
                read_robots.parse(robots_list)
            except:
                return False
            if read_robots.can_fetch("*", dest_url):
                return True
            else:
                spider.denied.append(dest_url)
                return False
        else:
            return False

    def valid_type(spider, dest_url):
        try:
            spider.wait()
            html_response = urlopener.open(dest_url)
        except:
            return False
        else:
            response = html_response.info()
            content_type = response.type
            for valid_type in status.allowed_type:
                if str(content_type).endswith(valid_type):
                    return True
            spider.denied.append(dest_url)  #mark as visited
            return False

    def process_url(spider, dest_url):
        parse_res = urlparse.urlparse(dest_url)
        for domain in spider.allowed_domain:
            if str(parse_res.hostname).endswith(domain):
                #a dup url,if not outgoing just skip it
                if dest_url in spider.frontier or dest_url in spider.visited:
                    if dest_url not in spider.outgoing:
                        spider.outgoing.append(dest_url)
                #new url,check if it's valid
                elif spider.valid_url(dest_url) and spider.valid_type(dest_url) and dest_url not in spider.denied:
                    spider.outgoing.append(dest_url)
                    spider.frontier.append(dest_url)
                    print dest_url
                    #print spider.frontier




parser = Search_NEU()
status = SpiderController()
urlopener = urllib.FancyURLopener({})

if __name__ == "__main__":
    start_time = time.time()
    #status.frontier.append("http://www.ccs.neu.edu")
    #as require should use args
    
    # Problem here
    # got socket error 54 whenever run into same url,
    # server is resetting my connect..damn
    status.frontier.append(sys.argv[1])
    while status.count < 100 and status.frontier:
        url = status.frontier.pop(0)
        #set () will do DFS
        
        #valid = False
        #spider.res = {}
        res = None
        #spider.denied = []
        #spider.outgoing = []
        try:
            #valid = status.valid_url(url)   let functions deal with it
            #if valid:
            ###############
            status.wait()
            res = urlopener.open(url)   #content-type inside
        except:
            continue
        else:
            #if valid and res:
                status.visited.append(url)
                parser.cur_url = url
                parser.this_seed(res)
                status.count += 1
                res.close()
#thanks to Yilin for guiding me about the output function
    with open("p2.txt", "w") as result:
        for key in status.visited:
            result.write(key + " ")
            for urls in status.res[key]:
                result.write(urls + " ")
            result.write("\n")