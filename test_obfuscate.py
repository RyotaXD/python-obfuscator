import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import obfuscate

SAMPLE = "import os\n\ndef f():\n    return 42\n\nprint(f())\n"


def run_payload(payload):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(payload)
        path = f.name
    proc = subprocess.run([sys.executable, path], capture_output=True, text=True)
    return proc.stdout, proc.stderr, proc.returncode


class TestGetSystemArch(unittest.TestCase):
    def check(self, machine, expected):
        with mock.patch("obfuscate.platform.machine", return_value=machine):
            self.assertEqual(obfuscate.get_system_arch(), expected)

    def test_x86_64_not_aarch64(self):
        # Bug: "64" in "x86_64" matched the aarch64 branch first.
        self.check("x86_64", "x86_64 (64-bit)")

    def test_aarch64(self):
        self.check("aarch64", "aarch64 (64-bit)")

    def test_arm64(self):
        self.check("arm64", "aarch64 (64-bit)")

    def test_armv7(self):
        self.check("armv7l", "armv7 (32-bit)")


class TestMarshalZlib(unittest.TestCase):
    def test_roundtrip(self):
        payload = obfuscate.build_marshal_zlib_payload(SAMPLE)
        out, err, rc = run_payload(payload)
        self.assertEqual(rc, 0, err)
        self.assertIn("42", out)


class TestMarshalV2(unittest.TestCase):
    def test_roundtrip_multistatement(self):
        # Bug: old code XORed the *source* and compiled it in 'eval' mode,
        # so any multi-statement script raised SyntaxError and no output
        # file was ever written. Stub also ignored the key.
        payload = obfuscate.build_marshal_v2_payload(SAMPLE)
        out, err, rc = run_payload(payload)
        self.assertEqual(rc, 0, err)
        self.assertIn("42", out)

    def test_explicit_key_roundtrip(self):
        payload = obfuscate.build_marshal_v2_payload(SAMPLE, key=200)
        self.assertIn("k = 200", payload)
        out, err, rc = run_payload(payload)
        self.assertEqual(rc, 0, err)
        self.assertIn("42", out)


if __name__ == "__main__":
    unittest.main()
