import numpy
import matplotlib.pyplot as plt
from scipy import stats
import json
import os

import nfdiaginit

statlog, verb = nfdiaginit.logs()


def create_dict(run_os, run_times, run_size):
    run_dict = {
        "platform": run_os,
        "elapsed": run_times,
        "size": run_size
    }
    return run_dict


def read_stats():
    statlog.debug("Opening file " + os.path.relpath("json/statistics.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/statistics.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        run_os = data["platform"]
        run_times = data["elapsed"]
        run_size = data["size"]

        return run_os, run_times, run_size

    except IOError:
        # print("warning")
        statlog.warning("Could not find or open file", exc_info=True)


def write_stats(run_dict):
    statlog.debug("Opening file " + os.path.relpath("json/statistics.json", nfdiaginit.cur_path))
    try:
        with open('json/statistics.json', 'w') as json_file:
            json.dump(run_dict, json_file)
    except IOError:
        statlog.warning("Could not find or open file", exc_info=True)


# noinspection PyCompatibility,PyCompatibility,PyCompatibility,PyCompatibility
def get_stats(platform, elapsed, size):
    run_os, run_times, run_size = read_stats()
    run_os.append(platform)
    run_times.append(elapsed)
    run_size.append(size)

    run_dict = create_dict(run_os, run_times, run_size)
    write_stats(run_dict)

    ave = numpy.mean(run_times)
    med = numpy.median(run_times)
    # z = stats.mode(run_times)
    dev = numpy.std(run_times)
    var = numpy.var(run_times)
    per = numpy.percentile(run_times, 80)
    # test = numpy.random.uniform(4.0, 8.0, 250)
    # xx = numpy.random.normal(size=4)
    # for item in test:
    #    run_times.append(item)

    # print(x,y,z,dev,var,per,test,xx)
    # write_stats(run_times)
    # noinspection PyCompatibility
    print("Average time: ", f'{ave:.4f}')
    print("80 Percentile: ", f'{per:.4f}')
    print("Std Dev time: ", f'{dev:.4f}')
    print("Median time: ", f'{med:.4f}')
    print("Variance time: ", f'{var:.4f}')

    fig = plt.figure()
    fig.suptitle('Average Times', fontsize=20)
    plt.hist(run_times, 100)
    plt.ylabel('Log Size')
    plt.xlabel('Run Times')
    plt.show()

    fig = plt.figure()
    fig.suptitle('Scatter Plot: Size, Times', fontsize=20)
    plt.scatter(run_size, run_times)
    plt.xlabel('Log Size')
    plt.ylabel('Run Times')
    plt.show()

    slope, intercept, r, p, std_err = stats.linregress(run_size, run_times)

    def myfunc(run_size):
        return slope * run_size + intercept

    mymodel = list(map(myfunc, run_size))

    fig = plt.figure()
    fig.suptitle('Linear Regression: Average Times', fontsize=20)
    plt.scatter(run_size, run_times)
    plt.plot(run_size, mymodel)
    plt.xlabel('Log Size')
    plt.ylabel('Run Times')
    plt.show()

    run_dict.clear()
