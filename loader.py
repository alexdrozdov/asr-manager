#!/usr/bin/env python
# -*- #coding: utf8 -*-

import sys
import os
sys.path.append('./coresystem')

import localdb
import core

def def_params(localdb):
    localdb.write_once("/db", None)

def init_database():
    localdb_path = "./localdb.pickle"
    try:
        localdb_path = os.environ['LOCALDB_PATH']
    except:
        pass
    localdb.init_localdb(localdb_path, def_params)

if __name__ == "__main__" :
    init_database()
    core.run()

