import unittest

import hark.guest


class TestGuest(unittest.TestCase):

    def testListGuests(self):
        g = hark.guest.guests()
        assert isinstance(g, list)
        assert len(g) > 0
