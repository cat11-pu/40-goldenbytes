import json
import threading
import unittest
import urllib.error
import urllib.request

from goldenbytes import Packer
from server import serve

class TestPacker(unittest.TestCase):
    def test_fixed_pack_roundtrip(self):
        packer = Packer()
        self.assertEqual(packer.unpack(packer.pack([1, 2])), [1, 2])

    def test_fixed_pack_width(self):
        self.assertEqual(len(Packer().pack([1])), 4)

    def test_truncated_fixed_raises(self):
        with self.assertRaises(ValueError):
            Packer().unpack(b"\x00\x01")

    def test_stats_shape(self):
        self.assertIn("version", Packer().stats())

    def test_http_fixed_pack(self):
        server = serve(0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % server.server_port
        with urllib.request.urlopen(base + "/pack", data=b'{"numbers": [1]}', timeout=5) as response:
            self.assertEqual(json.loads(response.read())["hex"], "00000001")
        server.shutdown()
