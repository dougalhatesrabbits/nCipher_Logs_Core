import re
import datetime
import os

import nfdiaginit

mylogs, verb = nfdiaginit.logs()


# noinspection PyCompatibility,PyCompatibility
def get_section(section):
    """
    Read the nfdiag.txt log file by section into a calling list
    Sections are deliminated by:
    -----BEGIN /opt/nfast/bin/hardserver type=RAW-----
    -----END /opt/nfast/bin/hardserver -----

    :param section:
    one of enquiry, nfdiag, hardserver, stattree, env
    :return: lines
    returns a list by nfdiag section
    """

    # noinspection PyCompatibility
    mylogs.debug(f"Mapping section {section}")
    found = bool(False)
    lines = []
    counter = 0

    args = nfdiaginit.get_args()
    logfile = args.file[0]

    try:
        mylogs.debug("Opening file " + os.path.abspath(logfile))
        with open(os.path.abspath(logfile)) as f:
            for num, line in enumerate(f, 1):
                x = re.search(r"^-----BEGIN.*" + r"" + section + r"(?!.--pool).*-----$", line)
                y = re.search(r"^-----END.*" + r"" + section + r"(?!.--pool).*-----$", line)
                # BEGIN
                if x:
                    # noinspection PyCompatibility
                    print(
                        f"{nfdiaginit.BColours.WARNING}\nYES! We have a match on {nfdiaginit.BColours.ENDC}" + section)
                    counter = num
                    # Remove whitespaces
                    lines.append(line.strip())
                    found = bool(True)
                elif not y and found:
                    if '#' in line[0]:
                        continue

                    # do not want to thrash a large hardserver log
                    if section not in ["hardserver.log", "hardserver"]:
                        # match = "not hs"
                        words = line.split()
                        first = words[0]

                        if first.isdigit():
                            word = words[1:]
                            line = " ".join(word)
                            lines.append(line)
                        else:
                            lines.append(line.strip())
                    else:
                        lines.append(line.strip())
                else:
                    found = bool(False)
        return lines, counter
    except IOError:
        # print("Could not open file " + f"{nfdiaginit.BColours.OKBLUE}" + nfdiaginit.args.file[0] + f"{nfdiaginit.BColours.ENDC} for reading")
        mylogs.error("Could not open file ", exc_info=True)
        exit(1)


def get_client_section(section):
    """
    Read the nfdiag.txt log file by section into a calling list
    Sections are deliminated by:
    -----BEGIN /opt/nfast/bin/hardserver type=RAW-----
    -----END /opt/nfast/bin/hardserver -----

    :param section:
    one of enquiry, nfdiag, hardserver, stattree, env
    :return: lines
    returns a list by nfdiag section
    """

    # noinspection PyCompatibility
    mylogs.debug(f"Mapping section {section}")
    found = bool(False)
    lines = []
    # counter = 0

    args = nfdiaginit.get_args()
    logfile = args.file[0]

    try:
        mylogs.debug("Opening file " + os.path.abspath(logfile))
        with open(os.path.abspath(logfile)) as f:
            for line in f:
                if '#' in line[0]:
                    continue

                begin = re.compile(r"^-----BEGIN" + r"(?!.*hsm-).*" + r"" + section + r".*-----$")
                end = re.compile(r"^-----END" + r"(?!.*hsm-).*" + r"" + section + r".*-----$")

                # BEGIN
                if begin.search(line):
                    # noinspection PyCompatibility
                    print(
                        f"{nfdiaginit.BColours.WARNING}\nYES! We have a match on Client {nfdiaginit.BColours.ENDC}" + section)

                    # counter = num
                    # Remove whitespaces
                    # lines.append(line.strip())
                    found = bool(True)
                elif not end.search(line) and found:

                    words = line.split()
                    first = words[0]

                    if first.isdigit():
                        word = words[1:]
                        line = " ".join(word)
                        lines.append(line)

                else:
                    found = bool(False)

        return lines
    except IOError:
        mylogs.error("Could not open file ", exc_info=True)
        exit(1)


def get_hsms():
    args = nfdiaginit.get_args()
    logfile = args.file[0]
    hsm_list = list()
    found = []
    pattern = '[A-Z,0-9]{4}-[A-Z,0-9]{4}-[A-Z,0-9]{4}'
    with open(logfile) as f:
        for lines in f:
            x = re.search(r"^-----BEGIN.*" + r"hsm-" + r".*-----$", lines)
            if x:
                found.append(lines.strip())
    for item in found:
        hsm = re.search(pattern, item).group()
        hsm_list.append(hsm)
    return hsm_list


# noinspection PyCompatibility
def get_hsm_section(section, hsm):
    """
    Read the nfdiag.txt log file by section into a calling list
    Sections are deliminated by:
    -----BEGIN /opt/nfast/bin/hardserver type=RAW-----
    -----END /opt/nfast/bin/hardserver -----

    :param hsm:
    :param section:
    one of enquiry, nfdiag, hardserver, stattree, env
    :return: lines
    returns a list by nfdiag section
    """

    # noinspection PyCompatibility
    mylogs.debug(f"Mapping section {hsm} {section}")
    found = bool(False)
    lines = []
    counter = 0

    args = nfdiaginit.get_args()
    logfile = args.file[0]

    try:
        mylogs.debug("Opening file " + os.path.abspath(logfile))
        with open(os.path.abspath(logfile)) as f:
            for num, line in enumerate(f, 1):
                x = re.search(r"^-----BEGIN.*" + r"hsm-" + r"" + hsm + r".*-----$", line)
                y = re.search(r"^-----END.*" + r"hsm-" + r"" + hsm + r".*-----$", line)
                # BEGIN
                if x:
                    print(f"{nfdiaginit.BColours.WARNING}\nYES! We have a match on HSM {nfdiaginit.BColours.ENDC}", hsm,
                          "", section)
                    counter = num
                    # Remove whitespaces
                    lines.append(line.strip())
                    found = bool(True)
                elif not y and found:
                    if '#' in line[0]:
                        continue

                    # do not want to thrash a large hardserver log
                    if section not in ["hardserver.log", "hardserver"]:
                        # match = "not hs"
                        words = line.split()
                        first = words[0]

                        if first.isdigit():
                            word = words[1:]
                            line = " ".join(word)
                            lines.append(line)
                    else:
                        lines.append(line.strip())
                else:
                    found = bool(False)
        return lines, counter
    except IOError:
        # print("Could not open file " + f"{nfdiaginit.BColours.OKBLUE}" + nfdiaginit.args.file[0] + f"{nfdiaginit.BColours.ENDC} for reading")
        mylogs.error("Could not open file ", exc_info=True)
        exit(1)


# noinspection PyCompatibility,PyCompatibility
def get_word(log, search, num):
    """
    Grep like search hardserver section (-o flag) omitting lines starting with a '#' and log dates older than a month.

    :param num:
    :param log:
    nfdiag log section list returned from get_section
    :param search:
    search pattern from JSON dictionary
    int 1 or 0, whole file or section search to toggle positional matches in file
    :return:
    found_list > a list of matched patterns
    """
    found_list = []
    # noinspection PyCompatibility,PyCompatibility
    mylogs.debug(f"Searching hardserver section for {search}")

    args = nfdiaginit.get_args()

    for counter, lines in enumerate(log, num):
        if re.findall(search, lines):
            num += 1
            line = lines.split()
            timestamp = line[1]
            pattern = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
            if not re.search(pattern, timestamp):
                continue
            date_time_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d')

            # Only want archive number of days logs to search
            previous_date = datetime.datetime.today() - datetime.timedelta(days=args.archive)
            if date_time_obj > previous_date:
                pointer = lines.find(search)
                lines = f"{nfdiaginit.BColours.OKBLUE}[L" + str(counter) + ",c" + str(
                    pointer) + "] " + f"{nfdiaginit.BColours.ENDC}" + lines
                print(lines)
                write(lines, "a")
                found_list.append(lines)
    return found_list


# noinspection PyCompatibility,PyCompatibility
def write(word, mode):
    mylogs.debug("Writing to file")

    try:
        file = open("nfdiag.out", mode)
        file.write(word)
        file.write("\n")
        file.close()
    except IOError:
        print("Could not write to " + f"{nfdiaginit.BColours.OKBLUE}nfdiag.out" + f"{nfdiaginit.BColours.ENDC}")
        mylogs.warning("Could not write to nfdiag.out", exc_info=True)
