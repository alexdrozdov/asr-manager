#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import os


def create_temporary_folder(prefix=None):
    def _tmp_name(prefix, time_str, tmp_index):
        return prefix+time_str+'-' + str(tmp_index)
    if None==prefix:
        prefix = './temporary/tmp-'
    time_str = time.asctime().replace(' ','_').replace(':','.')
    tmp_index = 0
    s = _tmp_name(prefix, time_str, tmp_index)
    while os.path.exists(s):
        tmp_index += 1
        s = _tmp_name(prefix, time_str, tmp_index)
    os.makedirs(s)
    return s+'/'
