#!/usr/bin/python
# -*- #coding: utf8 -*-

import traceback
import sys

class AdonRuntimeError(object):
    def __init__(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self.info = traceback.format_exc()
        tb_list = traceback.extract_tb(exc_traceback)
        last_error = tb_list[-1]
        self.source_file = last_error[0]
        self.line_number = last_error[1]
        self.func_name = last_error[2]
        self.cmd = last_error[3]
        self.exc_reason = traceback.format_exception_only(exc_type, exc_value)[0]
        self.exc_reason = self.exc_reason.replace('\n', '')

    def get_message(self):
        return self.info
    def get_source_file(self):
        return self.source_file
    def get_line_number(self):
        return self.line_number
    def get_func_name(self):
        return self.func_name
    def get_cmd(self):
        return self.cmd
    def get_reason(self):
        return self.exc_reason

