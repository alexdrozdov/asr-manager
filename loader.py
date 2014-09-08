#!/usr/bin/env python
# -*- #coding: utf8 -*-

import sys
sys.path.append('./coresystem')

import localdb
import core

def def_params(localdb):
    localdb.write_once("/db", None)

def init_database():
    localdb.init_localdb("localdb.pickle", def_params)

if __name__ == "__main__" :
    init_database()
    core.run()

