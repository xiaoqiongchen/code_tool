import os
import multiprocessing
import time
import re
import string
class Consumer(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
    def run(self):
        proc_name = self.name
        while True:
                next_task = self.task_queue.get()
                if next_task is None:
                    print(('%s: Exiting' % proc_name))
                    self.task_queue.task_done()
                    break
                else:
                    print(('%s: %s' % (proc_name, next_task)))
                    answer = next_task()
                    self.task_queue.task_done()
                    self.result_queue.put(answer)
        return
class Task(object):
    def __init__(self,path):
        self.path=path
    def __call__(self):
        dic = {}
        try:
            with open(self.path, 'r',encoding="utf-8") as fp:
                 data=fp.readlines()
                 spacecode=0
                 markcode=0
                 validcode=0
                 count=0
                 flag=False
                 for line in data:
                     if line.strip() in string.whitespace:
                         spacecode+=1
                     elif line.strip()[0]=="#":
                         markcode+=1
                     elif re.findall(r"^\'\'\'",line) and flag==False:
                         markcode+=1
                         flag=True
                     elif re.findall(r"^\'\'\'",line) and flag==True:
                         markcode+=1
                         flag=False
                     elif flag:
                        markcode+=1
                     else:
                         validcode+=1
                 dic["文件:"]=self.path
                 dic["代码总行"]=len(data)
                 dic["有效行"]=validcode
                 dic["空行"]=spacecode
                 dic["注释行"]=markcode
        except Exception as e:
               print("%s文件异常" %self.path)
        return dic
    def __str__(self):
            return "%s处理中" % (self.path)
if __name__ == '__main__':
    starttime=time.time()
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    num_consumers = multiprocessing.cpu_count()
    consumers = [Consumer(tasks, results) for i in range(num_consumers)]
    path = r"E:\\"
    count=0
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if os.path.splitext(file)[-1] == ".py":
                    tasks.put(Task(os.path.join(root, file)))
                    count+=1
    # 依次启动子进程
    for i in range(1):
        tasks.put(None)
    print(count)
    for w in consumers:
        w.start()
    tasks.join()
    totalcount=0
    vaildcount=0
    spacecount=0
    markcount=0
    while count:
        result = results.get()
        print('Result: %s' % result)
        for k,v in result.items():
            totalcount+=result["代码总行"]
            vaildcount+=result["有效行"]
            spacecount+=result["空行"]
            markcount+=result["注释行"]
            break
        count -= 1
    print("总代码数为：%s，有效行为：%s，空行为：%s，注释行为：%s" %(totalcount,vaildcount,spacecount,markcount))
    endtime=time.time()
    print("总耗时：%s" %(endtime-starttime))