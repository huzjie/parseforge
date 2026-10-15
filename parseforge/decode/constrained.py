"""Constrained decoder: enforce JSON-schema validity during generation.

The core idea of structured extraction: instead of asking the model to *write*
free prose and then reparsing it (error-prone), we constrain the token vocabulary
at each step to only those tokens that keep the partial output a valid JSON
prefix. This module provides:

* ``JSON_MASK`` -- the canonical allowed-character set of JSON;
* ``ConstrainedDecoder`` -- a deterministic finite-state validator that checks a
  partial JSON string and returns which structural states are still reachable.

The mock backend uses this to decide, for a given token, whether it would be
legal under the current schema state -- the mechanism a real constrained decoder
implements with a grammar + token masks.
"""

JSON_MASK = set('{}[]",:0123456789.+-eEtruefalsn ')


class ConstrainedDecoder:
    """Finite-state structural validator for partial JSON.

    States track: in-string, escape, depth, and whether the last significant
    character was a colon/comma. ``legal(char)`` tells the generator whether
    appending ``char`` keeps the string a valid JSON *prefix* (not full JSON --
    prefixes are allowed while the object is still being built).
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.depth = 0
        self.in_string = False
        self.escape = False
        self.expect_value = True  # start of document expects a value
        self.buf = []

    def legal(self, ch):
        # 1. inside a string: accept any printable char, honour escapes
        if self.in_string:
            if self.escape:
                self.escape = False
                return True
            if ch == "\\":
                self.escape = True
                return True
            if ch == '"':
                self.in_string = False
                return True
            return True

        # 2. whitespace is always allowed between structural tokens
        if ch in " \t\n\r":
            return True

        # 3. opening a string value
        if ch == '"':
            if not self.expect_value:
                return False
            self.in_string = True
            self.expect_value = False
            self.buf.append(ch)
            return True

        # 4. structural characters
        if ch in "{[":
            if not self.expect_value:
                return False
            self.depth += 1
            self.expect_value = True
            self.buf.append(ch)
            return True
        if ch in "}]":
            if self.depth == 0:
                return False
            self.depth -= 1
            self.expect_value = False
            self.buf.append(ch)
            return True
        if ch == ":":
            if self.expect_value:
                return False
            self.expect_value = True
            self.buf.append(ch)
            return True
        if ch == ",":
            if self.expect_value:
                return False
            self.expect_value = True
            self.buf.append(ch)
            return True

        # 5. scalar value characters (digits, letters of true/false/null, sign, dot)
        if ch in JSON_MASK:
            if not self.expect_value:
                return False
            self.expect_value = False
            self.buf.append(ch)
            return True
        return False

    def is_complete(self):
        """True if the buffer is a complete, balanced JSON document."""
        return (not self.in_string and not self.escape
                and self.depth == 0 and len(self.buf) > 0)
