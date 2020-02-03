import json
import os

import nfdiaginit

readlog, verb = nfdiaginit.logs()


def read_enquiry():
    """
    Read the JSON from 'enquiry.json' file into 2 dictionaries used for referencing items of interest during the
    next parsing of the nfdiag log section.

    :return:
    server_dict > a dictionary of log interests
    module_dict > a dictionary of log interests
    """

    server_dict = dict()
    module_dict = dict()

    readlog.debug("Opening file " + os.path.relpath("json/enquiry.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/enquiry.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        # JSON server dictionary
        for key in data["server"]:
            value = data["server"][key]
            server_dict[key] = value

        # JSON module dictionary
        for key in data["module"]:
            value = data["module"][key]
            module_dict[key] = value

        return server_dict, module_dict
    except IOError:
        # print("Could not find or open file " + new_path)
        # print(__doc__)
        readlog.warning("Could not find or open file", exc_info=True)


def read_nfkminfo():
    """
    Read the JSON from 'enquiry.json' file into 2 dictionaries used for referencing items of interest during the
    next parsing of the nfdiag log section.

    :return:
    world_dict  > a dictionary of log interests
    module_dict > a dictionary of log interests
    """
    world_dict = dict()
    module_dict = dict()

    readlog.debug("Opening file " + os.path.relpath("json/nfkminfo.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/nfkminfo.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        # JSON world dictionary
        for key in data["world"]:
            value = data["world"][key]
            world_dict[key] = value

        # JSON module dictionary
        for key in data["module"]:
            value = data["module"][key]
            module_dict[key] = value

        return world_dict, module_dict
    except IOError:
        # print("Could not find or open file " + new_path)
        # print(__doc__)
        readlog.warning("Could not find or open file", exc_info=True)


def read_hardserver():
    """
    Read the JSON from 'dictionary.json' file into a dictionary used for referencing items of interest during the
    next parsing of the nfdiag log section.

    :return:
    world_dict > a dictionary of log interests
    """
    hardserver_dict = dict()

    readlog.debug("Opening file " + os.path.relpath("json/dictionary.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/dictionary.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        # JSON world dictionary
        for key in data["hardserver"]:
            value = data["hardserver"][key]
            hardserver_dict[key] = value

        return hardserver_dict
    except IOError:
        # print("Could not find or open file " + new_path)
        # print(__doc__)
        readlog.warning("Could not find or open file", exc_info=True)


def read_env():
    """
    Read the JSON from 'dictionary.json' file into 2 lists used for referencing items of interest during the
    next parsing of the nfdiag log section.

    :return:
    windows_list > a list of log interests
    linux_list   > a list of log interests
    """

    readlog.debug("Opening file " + os.path.relpath("json/env.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/env.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        windows_list = data["Windows"]
        linux_list = data["Linux"]

        return windows_list, linux_list
    except IOError:
        # print("Could not find or open file " + new_path)
        # print(__doc__)
        readlog.warning("Could not find or open file", exc_info=True)
        # exit(1)


def read_fips():
    """
    Read the JSON from 'fips.json' file into a dictionary used for referencing items of interest during the
    next parsing of the nfdiag log section.

    :return:
    fips_dict > a dictionary of log interests
    """
    fips_dict = dict()

    readlog.debug("Opening file " + os.path.relpath("json/fips.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/fips.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        for key in data:
            value = data[key]
            fips_dict[key] = value
    except IOError:
        # print("Could not find or open file " + new_path)
        # print(__doc__)
        readlog.warning("Could not find or open file", exc_info=True)
        # exit(1)
    finally:
        return fips_dict


def read_stattree():
    """
    Read the JSON from 'dictionary.json' file into a dictionary used for referencing items of interest during the
    next parsing of the nfdiag log section.
    :return:
    stat_dict > a dictionary of log interests
    """
    stat_dict = dict()

    readlog.debug("Opening file " + os.path.relpath("json/dictionary.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/dictionary.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        for key in data["stattree"]:
            value = data["stattree"][key]
            stat_dict[key] = value

        return stat_dict
    except IOError:
        # print("Could not find or open file" + new_path)
        # print(__doc__)
        readlog.warning("Could not find or open file", exc_info=True)
        # exit(1)


def read_client_config():
    """
    Read the JSON from 'dictionary.json' file into a dictionary used for referencing items of interest during the
    next parsing of the nfdiag log section.
    :return:
    stat_dict > a dictionary of log interests
    """

    readlog.debug("Opening file " + os.path.relpath("json/dictionary.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/dictionary.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        config_list = data["client config"]

        return config_list
    except IOError:
        readlog.warning("Could not find or open file", exc_info=True)


def read_hsm_config():
    """
    Read the JSON from 'dictionary.json' file into a dictionary used for referencing items of interest during the
    next parsing of the nfdiag log section.
    :return:
    stat_dict > a dictionary of log interests
    """

    readlog.debug("Opening file " + os.path.relpath("json/dictionary.json", nfdiaginit.cur_path))
    try:
        new_path = os.path.relpath("json/dictionary.json", nfdiaginit.cur_path)
        with open(new_path) as f:
            data = json.load(f)

        config_list = data["hsm config"]

        return config_list
    except IOError:
        readlog.warning("Could not find or open file", exc_info=True)
