import base64
import os
import unittest

from src import gitops

github_pat = os.environ.get("DEPLOYMENT_TOKEN", "")


class TestGitops(unittest.TestCase):

    def test_getfile(self):
        client = gitops.ghclient(github_pat)
        _, file = gitops.get_file(client, "tests/service/test/values.yaml", "mashanm/argocd-promote", "main")
        self.assertEqual(file.content, "dGVzdAo=\n")

