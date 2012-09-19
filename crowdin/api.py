import io
import json
import logging
import requests
import zipfile

from xml.etree import ElementTree

logger = logging.getLogger('crowdin')


class CrowdinException(Exception):
    pass


class API(object):
    root_url = "http://api.crowdin.net/api"

    def __init__(self, project_name=None, api_key=None):
        self.project_name = project_name
        self.api_key = api_key

    def params(self, **params):
        params['key'] = self.api_key
        return params

    @property
    def project_url(self):
        return "{0}/project/{1}".format(self.root_url, self.project_name)

    @property
    def info_url(self):
        return "{0}/info".format(self.project_url)

    def info(self):
        logger.debug("Fetching project information")
        response = requests.get(self.info_url, params=self.params(json=True))
        if response.status_code != 200:
            raise CrowdinException(response.text)
        return json.loads(response.content)

    def exists(self, name, info=None):
        """
        Returns True if a remote path exists, False otherwise.
        """
        if info is None:
            info = self.info()

        dirs = name.split('/')
        for index, name in enumerate(dirs):
            for f in info['files']:
                if f['name'] == name:
                    info = f
                    break
            else:
                return False
        return True

    @property
    def mkdir_url(self):
        return '{0}/add-directory'.format(self.project_url)

    def mkdir(self, name):
        logger.debug("Creating remote directory {0}".format(name))
        response = requests.post(self.mkdir_url, params=self.params(name=name))
        parsed = ElementTree.fromstring(response.text)
        if parsed.tag != 'success':
            raise CrowdinException(response.text)

    @property
    def put_url(self):
        return '{0}/add-file'.format(self.project_url)

    @property
    def update_url(self):
        return '{0}/update-file'.format(self.project_url)

    @property
    def upload_translation_url(self):
        return '{0}/upload-translation'.format(self.project_url)

    def put(self, local, target, info=None, lang=None):
        """
        Uploads a translation file to a remote path.
        """
        if lang is None:
            logger.info("Uploading source translation {0} to {1}".format(
                local, target
            ))
        else:
            logger.info("Uploading {0} translation of {1} to {2}".format(
                lang, local, target
            ))
        if info is None:
            info = self.info()

        params = self.params()

        if lang is not None:
            url = self.upload_translation_url
            params['language'] = lang
        elif self.exists(target, info):
            url = self.update_url
        else:
            url = self.put_url

        with open(local, 'r') as f:
            files = {'files[{0}]'.format(target): f}
            response = requests.post(url, params=params, files=files)
        parsed = ElementTree.fromstring(response.text)
        if parsed.tag != 'success' or response.status_code != 200:
            raise CrowdinException(response.text)

    @property
    def translations_url(self):
        return '{0}/download/all.zip'.format(self.project_url)

    def translations(self):
        """
        Returns a ZipFile with all the available remote translations.
        """
        logger.info("Downloading translations")
        response = requests.get(self.translations_url, params=self.params())
        return zipfile.ZipFile(io.BytesIO(response.content))

    @property
    def export_url(self):
        return '{0}/export'.format(self.project_url)

    def export(self):
        logger.info("Exporting translations")
        response = requests.post(self.export_url, params=self.params())
        parsed = ElementTree.fromstring(response.text)
        if parsed.tag != 'success':
            raise CrowdinException(response.text)
