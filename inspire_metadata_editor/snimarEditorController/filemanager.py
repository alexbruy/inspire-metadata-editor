# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/filemanager.py
#  Authors: Pedro Dias, Eduardo Castanho, Joana Teixeira
#  Date:    2015-08-11T16:14:20
#
# ---------------------------------------------------------------------------
#
#  XML metadata editor plugin for QGIS developed for the SNIMar Project.
#  Copyright (C) 2015  Eduardo Castanho, Pedro Dias, Joana Teixeira
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import print_function
import os
import json
import datetime
from EditorMetadadosMarswInforbiomares import CONSTANTS
from EditorMetadadosMarswInforbiomares.CONSTANTS import FILELIST_STORE


class FileManager(dict):
    def __init__(self, to_save=False, *args, **kwargs):
        super(FileManager, self).__init__()
        editordir = kwargs.pop('editordir', None)
        if editordir is None:
            # fix_print_with_import
            print(u'Unable to create file list store')
        else:
            self.store = os.path.join(editordir, FILELIST_STORE)
            print(self.store)
        self.to_save = to_save

    def save(self):
        """Saves the current tracked files into a JSON file"""
        if not self.to_save:
            return
        try:
            fp = open(self.store, 'w')
            json.dump(self, fp)
            fp.close()
        except IOError:
            pass

    def track_new_file(self, *args, **kwargs):
        """Starts tracking a new file. Pass the id and title in the kwargs so
        it is guaranteed that the new file has the id and title also saved."""
        path = kwargs.pop('path', None)
        if path is not None and path not in self:
            self.setdefault(path, {})
        else:
            return False

        fo = self[path]
        fo['name'] = os.path.basename(path)
        fo['added'] = datetime.datetime.now().isoformat()
        fo['path'] = path
        fo['title'] = kwargs.pop('title', None)
        fo['id'] = kwargs.pop('id', None)
        fo['doc_type'] = kwargs.pop('doc_type', None)
        self.save()
        return True

    def load(self):
        """Loads the tracked files from a file"""
        data = None
        try:
            fp = open(self.store, 'r')
            data = json.load(fp)
            fp.close()
        except IOError:
            return False

        if data is not None:
            for key, value in list(data.items()):
                self.setdefault(key, value)
            return True

    def pop(self, k, d=None):
        ret = None
        try:
            ret = super(FileManager, self).pop(k)
            self.save()
        except KeyError:
            pass
        finally:
            return ret
