import json
import logging
import os
import tarfile

from aatest.check import END_TAG

__author__ = 'roland'

def setup_logging(logfile, log):
    hdlr = logging.FileHandler(logfile)
    base_formatter = logging.Formatter(
        "%(asctime)s %(name)s:%(levelname)s %(message)s")

    hdlr.setFormatter(base_formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)


def mk_tardir(issuer, test_profile):
    wd = os.getcwd()

    tardirname = wd
    for part in ["tar", issuer, test_profile]:
        tardirname = os.path.join(tardirname, part)
        if not os.path.isdir(tardirname):
            os.mkdir(tardirname)

    logdirname = os.path.join(wd, "log", issuer, test_profile)
    for item in os.listdir(logdirname):
        if item.startswith("."):
            continue

        ln = os.path.join(logdirname, item)
        tn = os.path.join(tardirname, "{}.txt".format(item))
        if not os.path.isfile(tn):
            os.symlink(ln, tn)


def create_tar_archive(issuer, test_profile):
    mk_tardir(issuer, test_profile)

    wd = os.getcwd()
    _dir = os.path.join(wd, "tar", issuer)
    os.chdir(_dir)

    tar = tarfile.open("{}.tar".format(test_profile), "w")

    for item in os.listdir(test_profile):
        if item.startswith("."):
            continue

        fn = os.path.join(test_profile, item)

        if os.path.isfile(fn):
            tar.add(fn)
    tar.close()
    os.chdir(wd)


def not_logging(logfile, logger):
    hdlr = logging.FileHandler(logfile)
    base_formatter = logging.Formatter(
        "%(asctime)s %(name)s:%(levelname)s %(message)s")

    hdlr.setFormatter(base_formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)


def get_test_info(session, test_id):
    return session["test_info"][test_id]


def pprint_json(json_txt):
    _jso = json.loads(json_txt)
    return json.dumps(_jso, sort_keys=True, indent=2, separators=(',', ': '))


def end_tags(info):
    _ll = info["trace"].lastline()

    try:
        if _ll.endswith(END_TAG) and info["test_output"][-1] == ("X", END_TAG):
            return True
    except IndexError:
        pass

    return False

def evaluate(session):
    try:
        if session["node"].complete:
            _info = session["test_info"][session["testid"]]
            if end_tags(_info):
                _sum = test_summation(_info["test_output"], session["testid"])
                session["node"].state = _sum["status"]
            else:
                session["node"].state = INCOMPLETE
        else:
            session["node"].state = INCOMPLETE
    except (AttributeError, KeyError):
        pass


def with_or_without_slash(path):
    if os.path.isdir(path):
        return path

    if path.endswith("%2F"):
        path = path[:-3]
        if os.path.isdir(path):
            return path
    else:
        path += "%2F"
        if os.path.isdir(path):
            return path

    return None
