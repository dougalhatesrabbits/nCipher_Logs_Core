import re
import datetime
import os
import configparser

import nfdiaginit
import nfdiagio

logthis, verbosity = nfdiaginit.logs()


def is_time_format(timestamp):
    """

    :param timestamp:
    :return:
    """
    logthis.debug("Checking if we have timestamp field f{timestamp}")
    try:
        datetime.datetime.strptime(timestamp, '%Y-%m-%d')
        # datetime.strptime(timestamp, '%Y-%m-%d')
        return True
    except ValueError:
        logthis.warning(f"We do not have a timestamp field {timestamp}", exc_info=True)
        return False


def parse_nfkminfo(log, world_dict, module_dict):
    """
    Parse the logic from the nfkminfo.json JSON file as detailed below:
    state: '!Initialised'       > any other value is OK
    mode: 'None'                > Is this FIPS? TBC
    state: '0x2 Usable'         > any other value is NOK

    :param log:
    nfdiag log section list returned from get_section
    :param world_dict:
    dictionary from JSON
    :param module_dict:
    dictionary from JSON
    :return:
    Output to screen and log file
    """

    logthis.debug("Reading nfkminfo section")

    world_keys = world_dict.keys()
    module_keys = module_dict.keys()
    output = ""
    write = ""

    # separate lists log:
    world_idx = log.index("World")
    module_idx = log.index("Module #1")
    world_list = log[world_idx:module_idx - 1]
    module_list = log[module_idx:]

    print(f"{nfdiaginit.BColours.HEADER}Nfkminfo{nfdiaginit.BColours.ENDC}")
    nfdiagio.write("\nNfkminfo\n********", "a")
    # Main Nfkminfo checks
    print(f"{nfdiaginit.BColours.UNDERLINE}" + world_list[0] + f"{nfdiaginit.BColours.ENDC}")
    for key in world_keys:
        for item in world_list:
            match = re.search(key, item)
            # Check for negative matches to JSON lists
            if match:
                value = world_dict[key]
                if type(value) is list:
                    found = False
                    for list_item in value:
                        if list_item in item:
                            found = True
                    if found:
                        out = nfdiaginit.Status(item, 70, 70, 5)
                        out.nok()
                        write = ('{:70}'.format(item) + '{:70}'.format("\n") + '{:5}'.format("[NOK]"))
                    else:
                        # output = ('{:70}'.format(item) + '{:5}'.format(f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                        out = nfdiaginit.Status(item, 70, 70, 5)
                        out.ok()
                        write = ('{:70}'.format(item) + '{:70}'.format("\n") + '{:5}'.format("[OK]"))

                elif value in item:
                    output = ('{:70}'.format(item) + '{:5}'.format(
                        f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                    write = ('{:70}'.format(item) + '{:5}'.format("[NOK]"))
                else:
                    output = ('{:70}'.format(item) + '{:5}'.format(
                        f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                    write = ('{:70}'.format(item) + '{:5}'.format("OK]"))

                if key == "mode":
                    items = item.split()
                    value = items[-1]
                    if value not in item:
                        output = ('{:20}'.format(key) + '{:50}'.format(value) + '{:5}'.format(
                            f"{nfdiaginit.BColours.OKGREEN}[FIPS]{nfdiaginit.BColours.ENDC}"))
                        write = ('{:20}'.format(key) + '{:50}'.format(value) + '{:5}'.format("[FIPS]"))
                    else:
                        output = ('{:20}'.format(key) + '{:50}'.format(value) + '{:5}'.format(
                            f"{nfdiaginit.BColours.FAIL}[NON FIPS]{nfdiaginit.BColours.ENDC}"))
                        write = ('{:20}'.format(key) + '{:50}'.format(value) + '{:5}'.format("[NON FIPS]"))
        print(output)
        nfdiagio.write(write, "a")

    print("\n" + f"{nfdiaginit.BColours.UNDERLINE}" + "Module & Slots" + f"{nfdiaginit.BColours.ENDC}")
    for key in module_keys:
        for item in module_list:
            match = re.search(key, item)

            # Check for positive matches to JSON lists
            if match:
                kvalue = module_dict.get(key)

                # Extra check for list of values
                if type(kvalue) is list:
                    # found = False
                    for list_item in kvalue:
                        if list_item in item:
                            output = ('{:20}'.format(key) + '{:70}'.format(list_item) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            print('{:20}'.format(key) + '{:50}'.format(list_item) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:20}'.format(key) + '{:50}'.format(list_item) + '{:5}'.format("[OK]"))
                            break
                elif kvalue in item:
                    output = ('{:70}'.format(item) + '{:5}'.format(
                        f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                    print('{:20}'.format(key) + '{:50}'.format(kvalue) + '{:5}'.format(
                        f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                    write = ('{:20}'.format(key) + '{:50}'.format(kvalue) + '{:5}'.format("[OK]"))
        # print(output)
        nfdiagio.write(write, "a")
        nfdiagio.write("\n", "a")


def parse_enquiry(log, server_dict, module_dict):
    """
    Parse the logic from the JSON file as detailed below:
    mode: operational              > any other value is NOK
    version: [versions]            > include valid current supported versions
    remote server port: '9004'     > highlight any non-default value
    serial number: '<14 spaces >'  > valid if not NULL
    module type code: [codes]      > identify module name and hardware status by module type
    kneti hash code: '<40 zeroes>' > any other value is OK
    hardware status: 'OK'          > any other value is NOK

    :param log:
    nfdiag log section list returned from get_section
    :param server_dict:
    dictionary from JSON
    :param module_dict:
    dictionary from JSON
    :return:
    Output to screen and log
    """

    logthis.debug("Reading enquiry section")

    # JSON
    module_keys = module_dict.keys()
    server_keys = server_dict.keys()
    module_name = ""

    module_list = dict()
    module_idx = dict()

    # Find Nr of modules to iterate thru
    str1 = ''.join(log)
    module_number = str1.count("Module #")

    # Create log dictionary
    for i in range(module_number):
        x = "Module #" + str(i + 1) + ":"
        module_list["module_list" + str(i + 1)] = x
        module_idx["module_idx" + str(i + 1)] = 0

    # Create Enquiry sublists from the log section
    # Need to evolve this for multiple modules! 8-)

    # Server first
    server_idx = log.index("Server:")
    module_idx1 = log.index(module_list["module_list1"])
    server_list = log[server_idx:module_idx1 - 1]

    # Now Module
    mymodulekeys = list(module_list)
    mymodulevalues = list(module_list.values())
    myidxkeys = list(module_idx)

    # Oh hell why not an iterator?
    for i in range(module_number):
        myidxkeys[i] = log.index(mymodulevalues[i])
        if i < module_number - 1:
            myidxkeys[i] = log.index(mymodulevalues[i])
            myidxkeys[i + 1] = log.index(mymodulevalues[i + 1])
            mymodulekeys[i] = log[myidxkeys[i]:myidxkeys[i + 1]]
            # print(mymodulekeys[i])
        else:
            mymodulekeys[i] = log[myidxkeys[i]:]
            # print(mymodulekeys[i])

    output = ""
    write = ""

    print(f"{nfdiaginit.BColours.HEADER}Enquiry{nfdiaginit.BColours.ENDC}")
    nfdiagio.write("Enquiry\n*******", "a")
    # Main Enquiry checks
    print(f"{nfdiaginit.BColours.UNDERLINE}" + server_list[0] + f"{nfdiaginit.BColours.ENDC}")
    for key in server_keys:
        key_found = str1.count(key)
        if not key_found:
            continue
        for item in server_list:
            matchkey = re.search(key, item)
            if key == "version":
                items = item.split()
                count = len(items)
                if count != 2:
                    continue
            # Check for positive matches to JSON lists
            if matchkey:
                value = server_dict[key]
                if type(value) is list:
                    for list_item in value:
                        if list_item in item:
                            output = ('{:30}'.format(key) + '{:30}'.format(list_item) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(list_item) + '{:5}'.format("[OK]"))
                            break
                        else:
                            # noinspection PyCompatibility,PyCompatibility
                            output = ('{:30}'.format(key) + '{:30}'.format(list_item) + '{:5}'.format(
                                f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(list_item) + '{:5}'.format("[NOK]"))
                elif value in item:
                    output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                        f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                    write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                else:
                    output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                        f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                    write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))
        print(output)
        nfdiagio.write(write, "a")

    # For each Module
    for i in range(module_number):
        print("\n" + f"{nfdiaginit.BColours.UNDERLINE}" + str(mymodulekeys[i][0]) + f"{nfdiaginit.BColours.ENDC}")
        # The search items (keys = mode, version, serial number....)
        for key in module_keys:
            key_found = str1.count(key)
            if not key_found:
                continue
            # Parse line by line the log module list
            for item in mymodulekeys[i]:
                match = re.search(key, item)
                if key == "mode":
                    items = item.split()
                    count = len(items)
                    if count != 2:
                        continue
                if key == "version":
                    items = item.split()
                    count = len(items)
                    if count != 2:
                        continue
                if key == "":
                    continue
                # Check for positive matches to JSON lists
                if match:
                    kvalue = module_dict.get(key)
                    # Extra check for list of values
                    if type(kvalue) is list:
                        for list_item in kvalue:
                            if list_item in item:
                                items = item.split()
                                value = items[-1]
                                output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                    f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                                write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                                break
                            else:
                                items = item.split()
                                value = items[-1]
                                output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                    f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                                write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))
                    elif kvalue in item:
                        items = item.split()
                        value = items[-1]
                        output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                            f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                        write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                    else:
                        items = item.split()
                        value = items[-1]
                        output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                            f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                        write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))

                    # Check for Null type values in JSON lists i.e. false positives
                    if key == "serial number":
                        items = item.split()
                        value = items[-1]
                        if value not in item:
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                        else:
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))
                    if key == "serial number":
                        pattern = '[A-Z,0-9]{4}-[A-Z,0-9]{4}-[A-Z,0-9]{4}'
                        items = item.split()
                        value = items[-1]
                        if re.search(pattern, value):
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                        else:
                            output = ('{:20}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))
                    if key == "kneti hash":
                        items = item.split()
                        value = items[-1]
                        if value not in item:
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                        else:
                            output = ('{:20}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:20}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))

                    if key == "kneti hash":
                        pattern = '[A-Z,0-9,a-z]{40}'
                        items = item.split()
                        value = items[-1]
                        if re.search(pattern, value):
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                        else:
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))

                    # check for USB driver status
                    if key == "hardware status":
                        items = item.split()
                        value = items[-1]
                        for modulecode in mymodulekeys[i]:

                            match = re.search("module type code", modulecode)
                            # Check for positive matches to JSON lists
                            if match:
                                module = modulecode.split()
                                moduletype = module[3]
                                if moduletype == "5":
                                    module_name = "nShield Edge"
                                elif moduletype == "12":
                                    module_name = "nShield Solo"
                                elif moduletype == "7":
                                    module_name = "nShield Connect"
                                else:
                                    module_name = "Unknown"

                        if kvalue not in item and moduletype == '12':
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                        elif value in item:
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.OKGREEN}[OK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[OK]"))
                        else:
                            output = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format(
                                f"{nfdiaginit.BColours.FAIL}[NOK]{nfdiaginit.BColours.ENDC}"))
                            write = ('{:30}'.format(key) + '{:30}'.format(value) + '{:5}'.format("[NOK]"))

            print(output)
            nfdiagio.write(write, "a")

        print("\nModule is a " + f"{nfdiaginit.BColours.OKBLUE}" + module_name + f"{nfdiaginit.BColours.ENDC}\n")
        nfdiagio.write("\nModule is a " + module_name + "\n", "a")


def parse_fips(log, fips_dict):
    """
    Parse the logic from the JSON file as detailed below:
    certification key: valid versions              > match version from module enquiry

    :param log:
    nfdiag log section list returned from get_section
    :param fips_dict:
    dictionary from JSON
    :return:
    Output to screen and log file
    """

    matchlist = []
    module_list = []

    logthis.debug("Reading fips dictionary")

    # noinspection PyUnusedLocal
    for logitem in log:
        module_idx = log.index("Module #1:")
        module_list = log[module_idx:]

    for item in module_list:
        match = re.search("version", item)
        # Check for positive matches to JSON lists
        if match:
            log_version = item.split()
            if len(log_version) == 2:
                log_version = log_version[1]
                matchlist.append(log_version)

    for item in matchlist:
        for key, value in fips_dict.items():
            if item in value:
                print("Module firmware version " + f"{nfdiaginit.BColours.OKBLUE}" + item + \
                      f"{nfdiaginit.BColours.ENDC} is likely candidate for " + f"{nfdiaginit.BColours.OKBLUE}" + key + f"{nfdiaginit.BColours.ENDC}")
                nfdiagio.write("Module firmware version " + item + " is likely candidate for " + key, "a")


def parse_stattree(log, stat_dict):
    """
    Parse the logic from the JSON file as detailed below:
    cpu: [CPU#]    > CPUs of interest
    fan: [FAN#]    > FANs of interest
    temp: [TEMP#]  > TEMPs of interest

    :param log:
    nfdiag log section list returned from get_section
    :param stat_dict:
    dictionary from JSON
    :return:
    Output to screen and log file
    """
    cpu_list = list()
    fan_list = list()
    temp_list = list()
    mem_list = list()
    globals_list = list()
    connections_list = list()

    # JSON world dictionary
    logthis.debug("Reading stattree section")
    # for key in stat_dict["cpu"]:
    for key in stat_dict.items():
        cpu_list = stat_dict.get("cpu")
        temp_list = stat_dict.get("temp")
        fan_list = stat_dict.get("fan")
        mem_list = stat_dict.get("mem")
        globals_list = stat_dict.get("globals")
        connections_list = stat_dict.get("connections")
        load_threshold = stat_dict.get("load_threshold")
        fan_threshold_high = stat_dict.get("fan_threshold_high")
        fan_threshold_low = stat_dict.get("fan_threshold_low")
        temp_threshold = stat_dict.get("temp_threshold")

    print('{:20}'.format("\ncpu#") + '{:10}'.format("%") + '{:10}'.format("status") + '{:20}'.format(
        "\n----") + '{:10}'.format("-") + '{:10}'.format("------"))
    nfdiagio.write('{:10}'.format("\ncpu#") + '{:10}'.format("%") + '{:10}'.format("status") + '{:10}'.format(
        "\n----") + '{:10}'.format("-") + '{:10}'.format("------"), "a")
    for item in cpu_list:
        for event in log:
            match = re.search(item, event)
            if match:
                cpu_performance = event.split()
                cpu_performance = cpu_performance[1]
                if int(cpu_performance) > load_threshold:
                    cpu_status = f"{nfdiaginit.BColours.FAIL}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
                    status = "NOK"
                else:
                    cpu_status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
                    status = "OK"
                print('{:20}'.format(item) + '{:10}'.format(cpu_performance) + '{:10}'.format(cpu_status))
                nfdiagio.write('{:10}'.format(item) + '{:10}'.format(cpu_performance) + '{:10}'.format(status), "a")

    print('{:20}'.format("\ncpu#") + '{:10}'.format("temp") + '{:10}'.format("status") + '{:20}'.format(
        "\n-------------") + '{:10}'.format("----") + '{:10}'.format("------"))
    nfdiagio.write('{:20}'.format("\ncpu#") + '{:10}'.format("temp") + '{:10}'.format("status") + '{:20}'.format(
        "\n----") + '{:10}'.format("----") + '{:10}'.format("------"), "a")
    for item in temp_list:
        for event in log:
            match = re.search(item, event)
            if match:
                cpu_temp = event.split()
                cpu_temp = float(cpu_temp[1])
                if cpu_temp > temp_threshold:
                    cpu_status = f"{nfdiaginit.BColours.FAIL}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
                    status = "NOK"
                else:
                    cpu_status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
                    status = "OK"
                print('{:20}'.format(item) + '{:10}'.format(cpu_temp) + '{:>20}'.format(cpu_status))
                nfdiagio.write('{:20}'.format(item) + '{:10}'.format(cpu_temp) + '{:10}'.format(status), "a")

    print('{:30}'.format("\nfan#") + '{:10}'.format("speed") + '{:10}'.format("status") + '{:30}'.format(
        "\n----") + '{:10}'.format("-----") + '{:10}'.format("-----"))
    nfdiagio.write('{:10}'.format("\nfan#") + '{:10}'.format("speed") + '{:10}'.format("status") + '{:10}'.format(
        "\n----") + '{:10}'.format("-----") + '{:10}'.format("-----"), "a")
    for item in fan_list:
        for event in log:
            match = re.search(item, event)
            if match:
                fan_speed = event.split()
                fan_speed = fan_speed[1]
                if int(fan_speed) > fan_threshold_high or int(fan_speed) < fan_threshold_low:
                    fan_status = f"{nfdiaginit.BColours.FAIL}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
                    status = "NOK"
                else:
                    fan_status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
                    status = "OK"
                print('{:30}'.format(item) + '{:10}'.format(fan_speed) + '{:10}'.format(fan_status))
                nfdiagio.write('{:10}'.format(item) + '{:10}'.format(fan_speed) + '{:10}'.format(status), "a")

    print('{:20}'.format("\nClients") + '{:10}'.format("#") + '{:10}'.format("status") + '{:20}'.format(
        "\n----") + '{:10}'.format("-") + '{:10}'.format("------"))
    nfdiagio.write('{:10}'.format("\nClients") + '{:10}'.format("#") + '{:10}'.format("status") + '{:10}'.format(
        "\n----") + '{:10}'.format("-") + '{:10}'.format("------"), "a")

    # Globals
    exported_list = list()
    args = nfdiaginit.get_args()
    logfile = args.file[0]
    with open(os.path.abspath(logfile)) as f:
        for lines in f:
            if re.findall('max exported modules', lines):
                lines = lines.split()
                number = lines[-1]
                exported_list.append(int(number))
    print(exported_list)
    # nfdiagio.write(exported_list, "a")
    client = list()
    max = list()
    for item in globals_list:
        if item == "ClientCount":
            for event in log:
                match = re.search(item, event)
                if match:
                    client_count = event.split()
                    client_count = client_count[1]
                    client.append(client_count)

        if item == "MaxClients":
            for event in log:
                match = re.search(item, event)
                if match:
                    max_clients = event.split()
                    max_clients = max_clients[1]
                    max.append(max_clients)

    if len(exported_list) > 1:
        exported_list.sort()
        maxes = exported_list[-1]
    else:
        maxes = exported_list[0]

    print("Found max client licences: " + str(maxes))
    nfdiagio.write("Found max client licences: " + str(maxes), "a")
    for i in range(len(client)):

        if int(client[i]) > maxes:
            global_status = f"{nfdiaginit.BColours.FAIL}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
            status = "NOK"

            print('{:20}'.format("ClientCount") + '{:10}'.format(client[i]) + '{:10}'.format(global_status))
            nfdiagio.write('{:10}'.format("ClientCount") + '{:10}'.format(client[i]) + '{:10}'.format(status), "a")

        else:
            global_status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
            status = "OK"

            print('{:20}'.format("ClientCount") + '{:10}'.format(client[i]) + '{:10}'.format(global_status))
            nfdiagio.write('{:10}'.format("ClientCount") + '{:10}'.format(client[i]) + '{:10}'.format(status), "a")

        if int(max[i]) > maxes:
            global_status = f"{nfdiaginit.BColours.FAIL}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
            status = "NOK"

            print('{:20}'.format("MaxClients") + '{:10}'.format(max[i]) + '{:10}'.format(global_status))
            nfdiagio.write('{:10}'.format("MaxClients") + '{:10}'.format(max[i]) + '{:10}'.format(status), "a")

        else:
            global_status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
            status = "OK"

            print('{:20}'.format("MaxClients") + '{:10}'.format(max[i]) + '{:10}'.format(global_status))
            nfdiagio.write('{:10}'.format("MaxClients") + '{:10}'.format(max[i]) + '{:10}'.format(status), "a")


def parse_hardserver(log, hardserver_dict, counter):
    """
    Parse the logic from the dictionary.json JSON file as detailed below:
    dict: ['values']   > return matches on 'value'

    :param counter:
    :param log:
    nfdiag log section list returned from get_section
    :param hardserver_dict:
    dictionary from JSON
    ;param flag:
    file or section
    :return:
    Output to screen and log file
    """
    hardserver_keys = hardserver_dict.keys()
    found_list = []
    found_dict = {}

    args = nfdiaginit.get_args()
    # logfile = args.file[0]

    logthis.debug("Reading hardserver section")
    print(f"{nfdiaginit.BColours.HEADER}Hardserver{nfdiaginit.BColours.ENDC}\n")
    nfdiagio.write("Hardserver\n**********", "a")
    # Main Hardserver checks
    print(f"{nfdiaginit.BColours.UNDERLINE}Show ALL hits in last " + str(
        args.archive) + " days" + f"{nfdiaginit.BColours.ENDC}")
    nfdiagio.write("\nShow ALL hits in last " + str(args.archive) + " days\n-----------------------------", "a")
    for key in hardserver_keys:
        value = hardserver_dict.get(key)
        for list_item in value:
            match_list = nfdiagio.get_word(log, list_item, counter)
            found_list.append(match_list)
            found_dict[list_item] = match_list

    print(f"{nfdiaginit.BColours.UNDERLINE}\nShow hit count{nfdiaginit.BColours.ENDC}")
    nfdiagio.write("\nShow hit count\n--------------", "a")
    for key, value in found_dict.items():
        count = len(value)
        if count > 0:
            print("found " + str(count) + " hits for " + key)
            nfdiagio.write("found " + str(count) + " hits for " + key, "a")

    print(f"\n{nfdiaginit.BColours.UNDERLINE}Show last hit only{nfdiaginit.BColours.ENDC}")
    nfdiagio.write("\nShow last hit only\n------------------", "a")
    for key, value in found_dict.items():
        count = len(value)
        if count > 0:
            print(value[-1])
            nfdiagio.write(value[-1], "a")


def parse_env(log, windows_list, linux_list):
    """
    Parse the logic from the dictionary.json JSON file as detailed below:
    Windows: ['values']  > Window OS identifiers
    Linux: ['values']    > Linux OS identifiers

    :param log:
    nfdiag log section list returned from get_section
    :param windows_list:
    Windows OS identifiers
    :param linux_list:
    Linux OS identifiers
    :return:
    Output to screen and log file
    """
    os = ""
    found = False

    logthis.debug("Reading env section")
    print(f"{nfdiaginit.BColours.HEADER}Environment{nfdiaginit.BColours.ENDC}")
    nfdiagio.write("\nEnvironment\n***********", "a")
    for line in log:
        for list_item in windows_list:
            if list_item in line:
                os = "Windows\n"
                found = True
        for list_item in linux_list:
            if list_item in line:
                os = "Linux\n"
                found = True
    if not found:
        print("OS is Unknown\n")
        nfdiagio.write("OS is Unknown", "a")
    else:
        print("OS is " + os)
        nfdiagio.write("OS is " + os, "a")


def parse_client_config(log, config_list):
    """
    Parse the logic from the dictionary.json JSON file as detailed below:
    dict: ['values']   > return matches on 'value'

    :param config_list:
    :param log:
    nfdiag log section list returned from get_section
    dictionary from JSON
    ;param flag:
    file or section
    :return:
    Output to screen and log file
    """
    # print(log)
    count = 0

    with open('client_config.ini', "w") as f:
        for lines in log:
            if '#' in lines:
                continue
            if '-----' in lines:
                continue
            if 'syntax' in lines:
                continue
            if 'local_module' in lines:
                count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'remote_ip' in lines:
                count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'remote_port' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'remote_esn' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'keyhash' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'timelimit' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'datalimit' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'privileged' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'privileged_use_high_port' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'ntoken_esn' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'native_path' in lines:
                count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'volume' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'allow_read' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'allow_write' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'allow_list' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'is_directory' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'is_text' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]

            f.write("%s\n" % lines)

    logthis.debug("Reading Client config section")
    print(f"{nfdiaginit.BColours.HEADER}Client Config{nfdiaginit.BColours.ENDC}\n")
    nfdiagio.write("Client Config\n**********", "w")
    parser = configparser.ConfigParser()
    parser.read('client_config.ini')
    for sect in parser.sections():
        if len(parser.items(sect)) > 0:
            print(f"{nfdiaginit.BColours.OKBLUE}Section:", sect, f"{nfdiaginit.BColours.ENDC}")
            for k, v in parser.items(sect):
                print(' {} = {}'.format(k, v))
            print()

    # noinspection PyBroadException
    try:
        if parser.has_option('server_settings', 'loglevel'):
            debug = parser.get('server_settings', 'loglevel')
            if debug in 'debug':
                status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
            else:
                status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
            print('{:15}'.format("Log Level"), '{:20}'.format(debug), '{:>30}'.format(status))
    except Exception:
        log.warning("Could not get log level", exc_info=True)

    if parser.has_option('server_startup', 'nonpriv_port'):
        nonpriv = parser.getint('server_startup', 'nonpriv_port')
        if nonpriv == 9000:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("Non Priv Port"), '{:20}'.format(nonpriv), '{:>30}'.format(status))

    if parser.has_option('server_startup', 'priv_port'):
        priv = parser.getint('server_startup', 'priv_port')
        if priv == 9001:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("Priv Port"), '{:20}'.format(priv), '{:>30}'.format(status))

    if parser.has_option('rfs_sync_client', 'remote_port'):
        remote_port = parser.getint('rfs_sync_client', 'remote_port')
        if remote_port == 9004:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("RFS Remote Port"), '{:20}'.format(remote_port), '{:>30}'.format(status))

    if parser.has_option('nethsm_imports', 'remote_port'):
        hsm_remote_port = parser.getint('nethsm_imports', 'remote_port')
        if hsm_remote_port == 9004:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("HSM Remote Port"), '{:20}'.format(hsm_remote_port), '{:>30}'.format(status))


def parse_hsm_config(log, config_list, hsm):
    """
    Parse the logic from the dictionary.json JSON file as detailed below:
    dict: ['values']   > return matches on 'value'

    :param hsm:
    :param config_list:
    :param log:
    nfdiag log section list returned from get_section
    dictionary from JSON
    ;param flag:
    file or section
    :return:
    Output to screen and log file
    """
    # print(log)
    count = 0

    with open(hsm + '.ini', "w") as f:
        for lines in log:

            # line = lines.split('=')
            # config.append(lines)
            if '#' in lines:
                continue
            if '-----' in lines:
                continue
            if 'syntax' in lines:
                continue
            if 'remote_ip' in lines:
                count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'remote_esn' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'keyhash' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'native_path' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'volume' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'allow_read' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'allow_write' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'allow_list' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'is_directory' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'is_text' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]

            if 'addr' in lines:
                count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'clientperm' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'esn' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'timelimit' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            if 'datalimit' in lines:
                # count += 1
                line = lines.split('=')
                lines = line[0] + str(count) + '=' + line[1]
            f.write("%s\n" % lines)

    logthis.debug("Reading HSM" + hsm + "config section")
    print(f"{nfdiaginit.BColours.HEADER}HSM " + hsm + f" Config{nfdiaginit.BColours.ENDC}\n")
    nfdiagio.write(hsm + " Config\n**********", "a")
    parser = configparser.ConfigParser()
    parser.read(hsm + '.ini')
    for sect in parser.sections():
        if len(parser.items(sect)) > 0:
            print(f"{nfdiaginit.BColours.OKBLUE}Section:", sect, f"{nfdiaginit.BColours.ENDC}")
            for k, v in parser.items(sect):
                print(' {} = {}'.format(k, v))
            print()

    # noinspection PyBroadException
    try:
        if parser.has_option('server_settings', 'loglevel'):
            debug = parser.get('server_settings', 'loglevel')
            if debug in 'debug':
                status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
            else:
                status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
            print('{:25}'.format("Log Level"), '{:20}'.format(debug), '{:>30}'.format(status))
    except Exception:
        log.warning("Could not get log level", exc_info=True)

    if parser.has_option('server_startup', 'nonpriv_port'):
        nonpriv = parser.getint('server_startup', 'nonpriv_port')
        if nonpriv == 9000:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("Non Priv Port"), '{:20}'.format(nonpriv), '{:>30}'.format(status))

    if parser.has_option('server_startup', 'priv_port'):
        priv = parser.getint('server_startup', 'priv_port')
        if priv == 9001:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("Priv Port"), '{:20}'.format(priv), '{:>30}'.format(status))

    if parser.has_option('rfs_sync_client', 'remote_port'):
        remote_port = parser.getint('rfs_sync_client', 'remote_port')
        if remote_port == 9004:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("RFS Remote Port"), '{:20}'.format(remote_port), '{:>30}'.format(status))

    if parser.has_option('nethsm_imports', 'remote_port'):
        hsm_remote_port = parser.getint('nethsm_imports', 'remote_port')
        if hsm_remote_port == 9004:
            status = f"{nfdiaginit.BColours.OKGREEN}[OK]" + f"{nfdiaginit.BColours.ENDC}"
        else:
            status = f"{nfdiaginit.BColours.WARNING}[NOK]" + f"{nfdiaginit.BColours.ENDC}"
        print('{:15}'.format("HSM Remote Port"), '{:20}'.format(hsm_remote_port), '{:>30}'.format(status))
