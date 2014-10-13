#!/usr/bin/env python
# -*- #coding: utf8 -*-

import sys
import os


coresystem_d = os.path.join(os.path.dirname(__file__),'coresystem')
if not os.path.exists(coresystem_d):
    raise RuntimeError("Couldnt find coresystem directory, exiting now...")
    exit(1)
sys.path.append(coresystem_d)

thirdparty = os.path.join(os.path.dirname(__file__),'thirdparty')
if os.path.exists(thirdparty):
    print "Extending search path to", thirdparty
    sys.path.append(thirdparty)

import localdb
import core

def def_params(localdb):
    localdb.write_once("/db", None)

def init_database():
    localdb_path = "./localdb.pickle"
    try:
        config_dir = os.environ['CONFIG_DIR']
        localdb_path = os.path.join(config_dir, 'localdb.pickle')
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
    except:
        pass
    try:
        localdb_path = os.environ['LOCALDB_PATH']
    except:
        pass
    localdb.init_localdb(localdb_path, def_params)

if __name__ == "__main__" :
    init_database()
    core.run()

