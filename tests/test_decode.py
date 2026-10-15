import unittest

from parseforge.decode.json_schema import Schema, validate
from parseforge.decode.constrained import ConstrainedDecoder


class TestDecode(unittest.TestCase):
    def test_schema_valid(self):
        schema = Schema.object({"a": {"type": "string"}})
        ok, _ = validate({"a": "x"}, schema)
        self.assertTrue(ok)

    def test_schema_invalid(self):
        schema = Schema.object({"a": {"type": "string"}})
        ok, err = validate({"a": 1}, schema)
        self.assertFalse(ok)

    def test_constrained_decoder(self):
        cd = ConstrainedDecoder()
        for ch in '{"a": 1}':
            self.assertTrue(cd.legal(ch))
        self.assertTrue(cd.is_complete())


if __name__ == "__main__":
    unittest.main()
