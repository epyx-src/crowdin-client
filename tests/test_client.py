import json
import logging
import mock
import os
import unittest
import shutil


from crowdin.client import push, pull

from tests import Crowdin_GET, Crowdin_POST

test_path = os.path.dirname(__file__)


class APITest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(
            stream=os.devnull
        )
        if os.path.exists("_data"):
            shutil.rmtree("_data")

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_push_ok(self, post, get):
        os.chdir(test_path)
        mock_get = Crowdin_GET(get, info={
            'files': [{
                'name': 'main',
                'files': [{
                    'name': 'simple',
                    'files': [{
                        'name': 'file.po'
                    }]
                }, {
                    'name': 'multi',
                    'files': [{
                        'name': 'good.po'
                    }, {
                        'name': 'good2.po'
                    }]
                }]
            }]
        })
        mock_post = Crowdin_POST(post)
        config_file = 'data/.crowdin.push.ok'
        with open(config_file, 'r') as f:
            conf = json.loads(f.read())

        push(conf, include_source=True)

        post_by_type = mock_post.call_by_type
        # Should not have performed 'add-directory':
        self.assertFalse('add-directory' in post_by_type)

        # Should not have performed 'add-file'
        self.assertFalse('add-file' in post_by_type)

        # Should have performed 'update-file' 3 times
        self.assertEqual(len(post_by_type['update-file']), 3)
        files = []
        for i in post_by_type['update-file']:
            files.extend(i['files'].keys())
        self.assertIn('files[main/simple/file.po]', files)
        self.assertIn('files[main/multi/good.po]', files)
        self.assertIn('files[main/multi/good2.po]', files)

        # Should only ask 'info' once.
        self.assertEqual(len(mock_get.calls), 1)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_push_create_dir(self, post, get):
        os.chdir(test_path)
        mock_get = Crowdin_GET(get, info={
            'files': []
        })
        mock_post = Crowdin_POST(post)
        config_file = 'data/.crowdin.push.ok'
        with open(config_file, 'r') as f:
            conf = json.loads(f.read())

        push(conf, include_source=True)

        post_by_type = mock_post.call_by_type
        get_by_type = mock_get.call_by_type

        # info called 3 times ( initial / upload single / upload multi )
        self.assertEqual(len(get_by_type['info']), 3)

        # Should have created 3 directory using 'add-directory'
        # create dir main is called twice, because /info does
        # not return the previously created dir ( test only )
        self.assertEqual(len(post_by_type['add-directory']), 4)
        added_dir = [x['params']['name']
                     for x in post_by_type['add-directory']]
        self.assertIn('main', added_dir)
        self.assertIn('main/simple', added_dir)
        self.assertIn('main/multi', added_dir)

        # Should have performed 'add-file' 3 times
        self.assertEqual(len(post_by_type['add-file']), 3)
        files = []
        for i in post_by_type['add-file']:
            files.extend(i['files'].keys())
        self.assertIn('files[main/simple/file.po]', files)
        self.assertIn('files[main/multi/good.po]', files)
        self.assertIn('files[main/multi/good2.po]', files)

    @mock.patch("requests.get")
    @mock.patch("requests.post")
    def test_pull_ok(self, post, get):
        os.chdir(test_path)
        mock_get = Crowdin_GET(get, info={
            'files': [{
                'name': 'main',
                'files': [{
                    'name': 'simple',
                    'files': [{
                        'name': 'file.po'
                    }]
                }, {
                    'name': 'multi',
                    'files': [{
                        'name': 'good.po'
                    }, {
                        'name': 'good2.po'
                    }]
                }]
            }]
        }, zip={
            'en/main/simple/file.po': 'data/sample.po',
            'fr/main/simple/file.po': 'data/sample.po',
            'en/main/multi/good.po': 'data/sample.po',
            'fr/main/multi/good.po': 'data/sample.po',
            'fr/main/multi/good2.po': 'data/sample.po',
        })
        mock_post = Crowdin_POST(post)
        config_file = 'data/.crowdin.pull.ok'
        with open(config_file, 'r') as f:
            conf = json.loads(f.read())

        pull(conf)

        post_by_type = mock_post.call_by_type

        # Should have called "export" to generate zip
        self.assertEqual(len(post_by_type['export']), 1)

        self.assertTrue(os.path.exists("_data/locale/en/simple/file.po"))
        self.assertTrue(os.path.exists("_data/locale/fr/simple/file.po"))
        self.assertTrue(os.path.exists("_data/locale/en/multi/good.po"))
        self.assertTrue(os.path.exists("_data/locale/fr/multi/good.po"))
        self.assertTrue(os.path.exists("_data/locale/fr/multi/good2.po"))

        self.assertFalse(os.path.exists("_data/locale/en/multi/good2.po"))

        # Should only ask 'download/all.zip' once.
        self.assertEqual(len(mock_get.calls), 1)
