import argparse
import json
import logging
import queue
import urllib.parse

import requests
API_BASE = "http://codeforces.com/api/"
def setup_logger():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

def api_call(method, parameters={}):
    response = requests.get(API_BASE+method, params=parameters)
    logging.warning("API CALL TO %s RETURNED STATUS CODE %s", method,response.status_code)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    else:
        logging.warning("API CALL TO %s RETURNED STATUS CODE %s", method, response.status_code)

def write_to_file(file,content):
    with open(file,'w',encoding="utf-8") as f:
        f.write(content)
        f.close()

q = queue.Queue()
class Task:
    def __init__(self,method,param):
        self.method = method
        self.param = param

    def do(self):
        content = api_call(self.method,self.param)
        # result = json.loads(content)
        param_encoded =urllib.parse.urlencode(self.param)
        # print(self.method+param_encoded)
        # print(content)
        write_to_file(self.method+param_encoded,content)


def request_loop():
    while not q.empty():
        item = q.get(False)
        item.do()
        q.task_done()
def main():
    setup_logger()
    logging.info("Starting To Operate")
    q.put(Task("contest.list",{}))
    request_loop()
    # content = api_call("contest.status",{"contestId":566,"from":1,"count":10})
    # result = json.loads(content)
    # a =urllib.parse.urlencode({"contestId":566,"from":1,"count":10})
    # write_to_file("content.status"+a,content)
    # print(result['status'])
    logging.info("Exisitng")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-s', dest='single', action='store_const',
                        const=True, default=True,
                        help='A single api call and saving result')

    parser.add_argument('--method', metavar='Method_Name', type=str,
                        help='Method name like contest.info')

    parser.add_argument('--args', metavar='Args', type=str, nargs='+',
                        help='Arguments')
    # parser.add_argument('--args', metavar='Arguments', type=str,
    #                     help='Arguments in URL encoded format')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')
    args = parser.parse_args()
    print(args.method)
    print(args.single)
    print(args.args)
    # main()