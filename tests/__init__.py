import itertools
import json
import os
import zipfile
import StringIO
from io import BytesIO as BaseBytesIO

from requests import Response

test_path = os.path.dirname(__file__)


class BytesIO(BaseBytesIO):
    def read(self, *args, **kwargs):
        kwargs.pop('decode_content', None)
        return super(BytesIO, self).read(*args, **kwargs)


class Patched(object):
    """
    Simple wrapper for mock to keep trace of the calls and
    check the result at the end
    """
    def __init__(self, mock, **kwargs):
        super(Patched, self).__init__()
        self.calls = []
        mock.side_effect = self
        self.kwargs = kwargs

    def __call__(self, url, files=None, params=None, *args, **kwargs):
        self.current_call = {
            'url': url,
            'files': files,
            'params': params,
            'type': url.split("/")[-1],
        }
        result = self.do_call(url,  *args, **kwargs)
        self.calls.append(self.current_call)
        return result

    def do_call(self, *args, **kwargs):
        pass

    @property
    def call_by_type(self):
        result = dict()
        self.calls.sort(key=lambda c: c['type'])
        for k, v in itertools.groupby(self.calls, key=lambda x: x['type']):
            result[k] = list(v)
        return result


class Crowdin_GET(Patched):

    def do_call(self, url, **kwargs):
        if url.endswith('/test-project/info'):
            response = Response()
            response.raw = BytesIO(
                json.dumps(self.kwargs.get('info', "")).encode('utf-8')
            )
            response.status_code = 200
            return response
        if url.endswith('/test-project/download/all.zip'):
            response = create_zip_response(self.kwargs.get('zip', {}))
            response.status_code = 200
            return response
        else:
            assert NotImplemented


class Crowdin_POST(Patched):

    def do_call(self, url, **kwargs):
        response = Response()
        response.raw = BytesIO(
            """<?xml version="1.0" encoding="ISO-8859-1"?>
                <success>
                </success>
            """.encode('utf-8'))
        response.status_code = 200
        return response


def create_zip_response(zip_info):
    response = Response()
    o = StringIO.StringIO()
    zf = zipfile.ZipFile(o, mode='w')
    for entry_name, file_name in zip_info.items():
        f = os.path.join(os.path.abspath(test_path), file_name)
        zf.write(f, entry_name)
    zf.close()
    o.seek(0)
    response._content = o.read()
    return response
