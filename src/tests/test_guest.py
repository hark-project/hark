import unittest

import hark.exceptions
import hark.guest
from hark.models.machine import Machine


class TestGuest(unittest.TestCase):
    def test_list_guests(self):
        g = hark.guest.guests()
        assert isinstance(g, list)
        assert len(g) > 0


class TestGuestConfig(unittest.TestCase):
    def test_guest_config(self):
        cfg = hark.guest.guest_config('Debian-8')

        assert cfg.virtualbox_os_type() == 'Debian_64'

        self.assertRaises(
            hark.exceptions.UnknownGuestException,
            hark.guest.guest_config, 'fjdklsjfsldj')


class TestSetupScript(unittest.TestCase):
    def test_setup_script(self):
        machine = Machine(
            machine_id='a', name='blahh',
            driver='virtualbox', guest='Debian-8',
            memory_mb=512)
        machine.validate()

        expect = "#!/bin/sh" \
            "\nset -ex" \
            "\nsudo sh -c \"echo 'blahh' > /etc/hostname\"" \
            "\nsudo sh -c \"echo 'blahh' > /etc/mailname\"" \
            "\nsudo hostname -F /etc/hostname\n"

        assert hark.guest.guest_config(
            'Debian-8').setup_script(machine) == expect
