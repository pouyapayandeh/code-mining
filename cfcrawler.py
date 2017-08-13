import argparse
import copy
import json
import logging
import queue
import urllib.parse
from time import sleep

import requests

API_BASE = "http://codeforces.com/api/"
COUNT_SIZE = 100
def setup_logger():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

def api_call(method, parameters={}):
    response = requests.get(API_BASE+method, params=parameters)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    else:
        print(response.content)
        logging.warning("API CALL TO %s with %s RETURNED STATUS CODE %s", method,parameters, response.status_code)

def write_to_file(file,content):
    file = file.replace("../","").replace("/","-")
    with open(file,'w',encoding="utf-8") as f:
        f.write(content)
        f.close()

q = queue.Queue()
class Task:
    def __init__(self,method,param , callback = None):
        self.method = method
        self.param = param
        self.callback = callback

    def do(self):
        logging.info("Started Task %s with %s", self.method, self.param)
        content = api_call(self.method,self.param)
        param_encoded =urllib.parse.urlencode(self.param)
        write_to_file(self.method+param_encoded,content)
        if self.callback != None:
            self.callback(self,content)


def request_loop():
    while not q.empty():
        logging.info("Queue Size = %s ",q.qsize())
        item = q.get(False)
        item.do()
        sleep(0.25)
        q.task_done()
def main():
    setup_logger()

    q.put(Task("contest.list",{}))
    request_loop()



def list_to_param(list):
    i = 0
    params = {}
    while i < len(list):
        print(list[i])
        params[list[i]] = list[i + 1]
        i += 2
    return params


def increment_page(t:Task,content):
    tt = copy.copy(t)
    tt.param['from'] +=COUNT_SIZE
    result = json.loads(content)
    # if len(result['result']) != 0:
    #     q.put(tt)
    for  x in result['result']:
        tp = Task("../contest/%s/submission/%s"%(x['contestId'],x['id']),{})
        q.put(tp)



if __name__ == "__main__":
    setup_logger()
    logging.info("Starting To Operate")
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-s', dest='single',action='store_const',const=True,
                         default=False,
                        help='A single api call and saving result')

    parser.add_argument('--method', metavar='Method_Name', type=str,
                        help='Method name like contest.info')

    parser.add_argument('--args', metavar='Args', type=str, nargs='+',
                        help='Arguments')

    parser.add_argument('-r', dest='range',action='store_const',const=True,
                        default=False,
                        help='A single api call and saving result')
    parser.add_argument('--start', metavar='Start Id', type=int,
                        help='Starting Contest Id')
    parser.add_argument('--finish', metavar='Finish Id', type=int,
                        help='Finishing Contest Id')

    args = parser.parse_args()
    if args.single:
        params = list_to_param(args.args)
        t = Task(args.method , params)
        t.do()
    elif args.range:
        logging.info("Starting Range Crawl")
        for x in range(args.start, args.finish):
            t = Task ('contest.status',{'contestId':x,'from':1,'count':COUNT_SIZE},increment_page)
            q.put(t)
        request_loop()
    logging.info("Exisitng")

# main()