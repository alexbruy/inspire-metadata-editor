from future import standard_library
standard_library.install_aliases()
from builtins import object
import re
import urllib.request, urllib.parse, urllib.error



class EmailValidator(object):
    def __init__(self):
        self.regex = re.compile(r'^.+@([^.@][^@]+)$', re.IGNORECASE)

    def is_valid(self, string):
        match = self.regex.match(string or '')
        if not match:
            return False
        else:
            return True
class URLValidator(object):
    def __init__(self):
        pass
    def is_valid(string):
        pass
