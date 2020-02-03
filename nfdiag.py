#!/usr/bin/env python3

##!/usr/bin/python

import sys
import time
import os
import colorama
from sys import platform
import threading
# noinspection PyCompatibility
import queue

import nfdiagread
import nfdiagparse
import nfdiaginit
import nfdiagio
import nfdiagstats

startTime = time.time()
colorama.init()
exitFlag = 0


# noinspection PyUnresolvedReferences
class NfdiagThread(threading.Thread):
    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    # noinspection PyUnresolvedReferences
    def get_client(self):
        # Client Config
        try:
            # noinspection PyUnresolvedReferences
            self.debug("Creating Client config lists")
            client_config = nfdiagio.get_client_section('config')
            if client_config:
                self.debug("Found Client config")
                client_config_list = nfdiagread.read_client_config()
                nfdiagparse.parse_client_config(client_config, client_config_list)
        except Exception:
            self.warning("Could not create Client config lists", exc_info=True)

    def get_hsm(self):
        # HSM Config
        try:
            self.debug("Creating HSM config lists")
            hsm_list = nfdiagio.get_hsms()
            for hsm in hsm_list:
                hsm_config, counter = nfdiagio.get_hsm_section('config', hsm)
                if hsm_config:
                    self.debug("Found HSM config")
                    hsm_config_list = nfdiagread.read_hsm_config()
                    nfdiagparse.parse_hsm_config(hsm_config, hsm_config_list, hsm)
        except Exception:
            self.warning("Could not create HSM config lists", exc_info=True)

    def get_env(self):
        try:
            self.debug("Creating env lists")
            windows_list, linux_list = nfdiagread.read_env()

            env, counter = nfdiagio.get_section('env')
            if env:
                self.debug("Found env")
                nfdiagparse.parse_env(env, windows_list, linux_list)
            env, counter = nfdiagio.get_section('system')
            if env:
                self.debug("Found env")
                nfdiagparse.parse_env(env, windows_list, linux_list)
            env, counter = nfdiagio.get_section('host')
            if env:
                self.debug("Found env")
                nfdiagparse.parse_env(env, windows_list, linux_list)
        except Exception:
            self.warning("Could not create env lists", exc_info=True)
            # exit(1)

    def get_enquiry(self):
        try:
            self.debug("Creating enquiry lists")
            enquiry, counter = nfdiagio.get_section('enquiry')
            if enquiry:
                self.debug("Found enquiry")
                # Read JSON dictionary files
                server_dict, module_dict = nfdiagread.read_enquiry()
                # Parse sections. Do the heavy lifting 8-)
                nfdiagparse.parse_enquiry(enquiry, server_dict, module_dict)

                fips_dict = nfdiagread.read_fips()
                nfdiagparse.parse_fips(enquiry, fips_dict)
        except Exception:
            self.warning("Could not create enquiry lists", exc_info=True)
            # exit(1)

    def get_stattree(self):
        try:
            self.debug("Creating stattree lists")
            stattree, counter = nfdiagio.get_section('stattree')
            if stattree:
                self.debug("Found stattree")
                stat_dict = nfdiagread.read_stattree()
                nfdiagparse.parse_stattree(stattree, stat_dict)
        except Exception:
            self.warning("Could not create stattree lists", exc_info=True)
            # exit(1)

    def get_nfkminfo(self):
        try:
            self.debug("Creating nfkminfo lists")
            nfkminfo, counter = nfdiagio.get_section('nfkminfo')
            if nfkminfo:
                self.debug("Found nfkminfo")
                world_dict, module_dict = nfdiagread.read_nfkminfo()
                nfdiagparse.parse_nfkminfo(nfkminfo, world_dict, module_dict)
        except Exception:
            self.warning("Could not create nfkminfo lists", exc_info=True)
            # exit(1)

    def get_hardserver(self):
        try:
            self.debug("Creating hardserver lists")
            hardserver, counter = nfdiagio.get_section('hardserver')
            if hardserver:
                self.debug("Found hardserver")
                hardserver_dict = nfdiagread.read_hardserver()
                nfdiagparse.parse_hardserver(hardserver, hardserver_dict, counter)
        except Exception:
            self.warning("Could not create hardserver lists", exc_info=True)
            # exit(1)

    def run(self):
        print("Starting " + self.name)
        process_data(self.name, self.q)
        # print("Exiting " + self.name)


# noinspection PyUnusedLocal
def process_data(thread_name, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            # noinspection PyUnusedLocal
            data = q.get()
            queueLock.release()
            # print("%s processing %s\n" % (thread_name, data))
        else:
            queueLock.release()
        # time.sleep(0.1)


print(nfdiaginit.BColours.CLEARSCREEN)
log, verb = nfdiaginit.logs()
log.setLevel(verb)

nfdiagio.write("Results", "w")
nfdiagio.write("=======\n", "a")

client = NfdiagThread.get_client
hsm = NfdiagThread.get_hsm
env = NfdiagThread.get_env
enquiry = NfdiagThread.get_enquiry
stattree = NfdiagThread.get_stattree
nfkminfo = NfdiagThread.get_nfkminfo
hardserver = NfdiagThread.get_hardserver

thread_list = ["Thread-1", "Thread-2", "Thread-3"]
func_list = [client, hsm, env, enquiry, stattree, nfkminfo, hardserver, ]
queueLock = threading.Lock()
workQueue = queue.Queue(10)
threading_list = []

# Create new threads
for tname in thread_list:
    thread = NfdiagThread(tname, workQueue)
    thread.start()
    threading_list.append(thread)

# Fill the queue
queueLock.acquire()
for function in func_list:
    workQueue.put(function(log))
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threading_list:
    t.join()
# print("Exiting Main Thread")


if __name__ == "__main__":
    logs, verbosity = nfdiaginit.logs()
    logs.setLevel(verbosity)
    logs.info("{0}, {1}, {2}".format(sys.executable, sys.argv[0], sys.argv[1:]))
    args = nfdiaginit.get_args()

    nfdiag = NfdiagThread("nfdiag", workQueue)
    nfdiag.run()

    # noinspection PyCompatibility
    elapsed = f'{time.time() - startTime:.2f}'
    # noinspection PyCompatibility
    size = f'{os.path.getsize(args.file[0]) / (1024 * 1024):.2f}'
    # noinspection PyCompatibility
    print("\nScript " + os.path.basename(
        __file__) + " took " + f"{nfdiaginit.BColours.HEADER}" + elapsed + f"{nfdiaginit.BColours.ENDC}" + " seconds")
    print('Log size: ', size, ' Mb')

    # wait
    if platform == "linux" or platform == "linux2":
        # linux
        print("Linux")
    elif platform == "darwin":
        # OS X
        print("OS X")
    elif platform == "win32":
        # Windows...
        os.system("pause")

    if args.statistics:
        nfdiagstats.get_stats(platform, float(elapsed), float(size))
