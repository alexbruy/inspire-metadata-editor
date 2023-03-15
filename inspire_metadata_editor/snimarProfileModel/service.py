# -*- coding=utf-8 -*-
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import os
import json
import urllib.request, urllib.error, urllib.parse
from qgis.PyQt.QtWidgets import QApplication

from urllib.parse import urljoin


BASE_URL = 'http://collab-keywords.snimar.pt/service/'
URL_ENDPOINT_LIST = (
    ("instrument", "Instrumento"),
    ("platform", "Plataforma"),
    ("place", "Toponímia"),
    ("project", "Projeto"),
    ("stratum", "Estrato"),
    # ("temporal"  , "Temporal"   ),
    ("taxon", "Taxonomia"),
)


def get_service_version():
    stable = {}
    unstable = {}
    try:
        response = urllib.request.urlopen(os.path.join(BASE_URL, 'version/?format=json'))
        json_data = json.loads(response.read())

        if len(json_data) <= 1:
            stable["version"] = "v.0.0"
            stable["version_date"] = "2115-10-06T08:44:58.739107Z"
        else:
            stables = [x for x in json_data if x.get("version") != "unstable"]
            stables.sort(key=lambda x: x.get("version"))
            stable = stables[-1]
        unstable = [x for x in json_data if x.get("version") == "unstable"][0]
    except urllib.error.HTTPError as e:
        # fix_print_with_import
        print("ERROR", e.reason())
    except IndexError:
        # fix_print_with_import
        print("ERROR", 'JSON malformed')
    except KeyError:
        # fix_print_with_import
        print("ERROR", 'JSON missing version field')
    finally:
        return {"stable": {"version": stable.get("version"), "version_date": stable.get("version_date")},
                "unstable": {"version_date": unstable.get("version_date", "2115-10-06T08:44:58.739107Z")}}


class ThesaurusServiceManager(object):
    def __init__(self, progress_bar):
        self.progress_bar = progress_bar
        self.value = 0

        self.latest_stable_version = None
        self.stable_date = None
        self.latest_unstable_version_date = None

        self.stable_data = {}
        self.unstable_data = {}
        QApplication.processEvents()

    def set_version_params(self):
        versions = get_service_version()
        self.latest_stable_version = versions["stable"]["version"]
        self.stable_date = versions["stable"]["version_date"]
        self.latest_unstable_version_date = versions["unstable"]["version_date"]
        if self.progress_bar:
            self.update_progress_bar()
        QApplication.processEvents()

    def retrieve_all(self):
        self.set_version_params()
        QApplication.processEvents()
        # buf = self.retrieve_disc_param(self.latest_stable_version)
        # if len(buf) > 0:
        #    self.stable_data.update(buf)

        # for endpoint in URL_ENDPOINT_LIST:
        #    buf = self.retrieve_from_list(endpoint[0], self.latest_stable_version)
        #    if buf is not None:
        #        self.stable_data.update(buf)

        # self.stable_data['version'] = self.latest_stable_version
        # self.stable_data['stable_version'] = self.latest_stable_version
        # self.stable_data['last_update'] = self.last_update
        buf = self.retrieve_disc_param(None)
        if len(buf) > 0:
            self.unstable_data.update(buf)

        for endpoint in URL_ENDPOINT_LIST:
            buf = self.retrieve_from_list(endpoint[0], None)
            if buf is not None:
                self.unstable_data.update(buf)
        self.unstable_data['stable_version'] = self.latest_stable_version
        self.unstable_data['version'] = self.latest_stable_version[0:-1] + 'x'
        self.unstable_data['last_update'] = self.latest_unstable_version_date
        return True

    def retrieve_from_list(self, endpoint, version):
        if version:
            url = os.path.join(os.path.join(BASE_URL, version), endpoint)
        else:
            url = os.path.join(BASE_URL, endpoint)

        try:
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            return data
        except urllib.error.HTTPError as e:
            # fix_print_with_import
            print("ERROR:",e.reason())
            return None
        finally:
            if self.progress_bar:
                self.update_progress_bar()

    def retrieve_disc_param(self, version):
        """
        Retrieve the discipline and discipline_parameter from the ckw web service. If
        a version is given, it is used, otherwise we retrieve the unstable version
        of the thesaurus.
        """
        if version:
            url = os.path.join(os.path.join(BASE_URL, version), 'discipline_parameter')
        else:
            url = os.path.join(BASE_URL, 'discipline_parameter')

        dp_data = {}
        try:
            response = urllib.request.urlopen(url)
            dp_data = json.loads(response.read())
        except urllib.error.HTTPError as e:
            # fix_print_with_import
            print("ERROR:",e.reason())
            return dp_data
        finally:
            if self.progress_bar:
                self.update_progress_bar()

        if version:
            url = os.path.join(os.path.join(BASE_URL, version), 'discipline')
        else:
            url = os.path.join(BASE_URL, 'discipline')

        try:
            response = urllib.request.urlopen(url)
            d_data = json.loads(response.read())
        except urllib.error.HTTPError as e:
            # fix_print_with_import
            print("ERROR:",e.reason())
            return {}
        finally:
            if self.progress_bar:
                self.update_progress_bar()

        dp_data['disciplines']['name_pt'] = d_data['discipline']['name_pt']
        for keyword, discipline in d_data['discipline']['keywords'].items():
            term_word = discipline['term_word']
            dp_data['disciplines'][term_word].update(discipline)

        return dp_data

    def update_progress_bar(self):
        self.value += 5
        self.progress_bar.setValue(self.value)
        QApplication.processEvents()


class WormsThesaurusManager(object):
    BASE_URL = 'https://www.marinespecies.org/rest'

    def search_by_aphia_id(self, identifier):
        """
        Runs a search query using a specific AphiaId.
        """
        url = urljoin(self.BASE_URL, '/'.join(['AphiaVernacularsByAphiaID', identifier]))

    def search_by_scientific_name(self, name, like=False):
        """
        Runs a search query using a given scientific name.
        """
        url = urljoin(self.BASE_URL, 'AphiaRecordsByNames')

        params = {
            'like': like,
            'marine_only': True,
            'scientificnames[]': name,
        }


class CrossRefThesaurusManager(object):
    pass
