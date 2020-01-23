
# All right reserved

import matplotlib
import requests
from bs4 import BeautifulSoup
import time,sched
import atexit
import pickle
import matplotlib.pyplot as plt
from datetime import datetime
import json
delays = 600

def get_current(counts,s):
    URL = 'https://3g.dxy.cn/newh5/view/pneumonia'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id='root')

    summary ={}
    # find the tables containing all info
    job_elems = results.find_all('div', class_='descBox___3dfIo')
    for job_elem in job_elems:
        for elem in job_elem:
            # print(elem)
            # province = elem.find('i',class_='orange___1FP2_')
            result = elem.select_one("span")
            stats = result.text.replace('，',' ').split(" ")
            print(stats)
            province = stats[0]
            summary[province] = {}
            try:
                index = stats.index('确诊')
                summary[province]["exact"]=int(stats[index+1])
                # print(summary[province]["exact"])
            except ValueError:
                # print("Province "+ province +" does not have "+ "确诊病例.")
                summary[province]["exact"] = None


            try:
                index = [i for i, s in enumerate(stats) if "疑似" in s][0]
                summary[province]["possible"] = int(stats[index+1])
                # print(summary[province]["possible"])
            except IndexError:
                summary[province]["possible"] = None
                # print("疑似 no value provided for"+ province)
            except ValueError:
                summary[province]["possible"] = None

            try:
                index = [i for i, s in enumerate(stats) if "死亡" in s][0]
                summary[province]["death"] = int(stats[index+1])
                # print(summary[province]["possible"])
            except IndexError:
                summary[province]["death"] = None
                # print("疑似 no value provided for"+ province)

            try:
                index = [i for i, s in enumerate(stats) if "治愈" in s][0]
                # print(index)
                summary[province]["cured"] = int(stats[index+1])
                # print(summary[province]["possible"])
            except IndexError:
                summary[province]["cured"] = None
                # print("疑似 no value provided for"+ province)

    total = results.find_next("span",class_="content___2hIPS").text.split(" ")
    exact = int(total[1])
    possible = int(total[4])
    cured = int(total[7])
    death = int(total[10])

    ts = time.time()
    counts[ts] = {"text":total,"exact":exact,"possible":possible,"cured":cured, "death":death,"summary":summary}
    print(counts[ts])
    ys = [counts[key]["exact"] for key in counts]
    xs = [datetime.fromtimestamp(int(float(t))) for t in list(counts.keys())]
    # print(counts.keys())
    # print(ys)


    ax = plt.gca()
    # xfmt = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
    # ax.xaxis.set_major_formatter(xfmt)
    fig = plt.figure()
    plt.plot(xs, ys, '*-')
    plt.xlabel("Date")
    plt.ylabel("Totol number")
    # plt.yscale("log")
    plt.title("Trend of coronavirus")
    plt.gcf().autofmt_xdate()

    # plt.show()
    fig.savefig("fig.png")
    plt.close()


    s.enter(delays,1,get_current, (counts,s))

if __name__=="__main__":
    try:
        with open('counts.pkl', 'r') as fp:
            counts = json.load(fp)
    except FileNotFoundError:
        counts ={}

    def exit_handler():
        print('My application is ending, saving data!')
        with open('counts.pkl', 'w') as f:
            json.dump(counts, f)
    atexit.register(exit_handler)


    s = sched.scheduler(time.time, time.sleep)
    s.enter(delays,1,get_current,(counts,s))
    s.run()













