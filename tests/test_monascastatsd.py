# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -*- coding: utf-8 -*-

"""Tests for monascastatsd.py."""

import collections
import socket
import time
import unittest

import monascastatsd.monasca_statsd


class FakeSocket(object):

    """A fake socket for testing."""

    def __init__(self):
        self.payloads = collections.deque()

    def send(self, payload):
        self.payloads.append(payload)

    def recv(self):
        try:
            return self.payloads.popleft()
        except IndexError:
            return None

    def __repr__(self):
        return str(self.payloads)


class BrokenSocket(FakeSocket):

    def send(self, payload):
        raise socket.error("Socket error")


class TestMonStatsd(unittest.TestCase):

    def setUp(self):
        self.monascastatsd = monascastatsd.monasca_statsd.MonascaStatsd()
        self.monascastatsd.socket = FakeSocket()

    def recv(self):
        return self.monascastatsd.socket.recv()

    def test_set(self):
        self.monascastatsd.set('set', 123)
        assert self.recv() == 'set:123|s'

    def test_gauge(self):
        self.monascastatsd.gauge('gauge', 123.4)
        assert self.recv() == 'gauge:123.4|g'

    def test_counter(self):
        self.monascastatsd.increment('page.views')
        self.assertEqual('page.views:1|c', self.recv())

        self.monascastatsd.increment('page.views', 11)
        self.assertEqual('page.views:11|c', self.recv())

        self.monascastatsd.decrement('page.views')
        self.assertEqual('page.views:-1|c', self.recv())

        self.monascastatsd.decrement('page.views', 12)
        self.assertEqual('page.views:-12|c', self.recv())

    def test_histogram(self):
        self.monascastatsd.histogram('histo', 123.4)
        self.assertEqual('histo:123.4|h', self.recv())

    def test_gauge_with_dimensions(self):
        self.monascastatsd.gauge('gt', 123.4,
                                 dimensions=['country:china',
                                             'age:45',
                                             'color:blue'])
        self.assertEqual("gt:123.4|g|#[" +
                         "'country:china', " +
                         "'age:45', " +
                         "'color:blue']",
                         self.recv())

    def test_counter_with_dimensions(self):
        self.monascastatsd.increment('ct',
                                     dimensions=['country:canada',
                                                 'color:red'])
        self.assertEqual("ct:1|c|#['country:canada', 'color:red']",
                         self.recv())

    def test_histogram_with_dimensions(self):
        self.monascastatsd.histogram('h', 1, dimensions=['color:red'])
        self.assertEqual("h:1|h|#['color:red']", self.recv())

    def test_sample_rate(self):
        self.monascastatsd.increment('c', sample_rate=0)
        assert not self.recv()
        for _ in range(10000):
            self.monascastatsd.increment('sampled_counter', sample_rate=0.3)
        self.assert_almost_equal(3000,
                                 len(self.monascastatsd.socket.payloads),
                                 150)
        self.assertEqual('sampled_counter:1|c|@0.3', self.recv())

    def test_samples_with_dimensions(self):
        for _ in range(100):
            self.monascastatsd.gauge('gst',
                                     23,
                                     dimensions=['status:sampled'],
                                     sample_rate=0.9)

        def test_samples_with_dimensions(self):
            for _ in range(100):
                self.monascastatsd.gauge('gst',
                                         23,
                                         dimensions=['status:sampled'],
                                         sample_rate=0.9)
            self.assertEqual('gst:23|g|@0.9|#status:sampled')

    def test_timing(self):
        self.monascastatsd.timing('t', 123)
        self.assertEqual('t:123|ms', self.recv())

    @staticmethod
    def assert_almost_equal(a, b, delta):
        assert 0 <= abs(a - b) <= delta, "%s - %s not within %s" % (a,
                                                                    b,
                                                                    delta)

    def test_socket_error(self):
        self.monascastatsd.socket = BrokenSocket()
        self.monascastatsd.gauge('no error', 1)
        assert True, 'success'

    def test_timed(self):

        @self.monascastatsd.timed('timed.test')
        def func(a, b, c=1, d=1):
            """docstring."""
            time.sleep(0.5)
            return (a, b, c, d)

        self.assertEqual('func', func.__name__)
        self.assertEqual('docstring.', func.__doc__)

        result = func(1, 2, d=3)
        # Assert it handles args and kwargs correctly.
        self.assertEqual(result, (1, 2, 1, 3))

        packet = self.recv()
        name_value, type_ = packet.split('|')
        name, value = name_value.split(':')

        self.assertEqual('ms', type_)
        self.assertEqual('timed.test', name)
        self.assert_almost_equal(0.5, float(value), 0.1)

    def test_batched(self):
        self.monascastatsd.open_buffer()
        self.monascastatsd.gauge('page.views', 123)
        self.monascastatsd.timing('timer', 123)
        self.monascastatsd.close_buffer()

        self.assertEqual('page.views:123|g\ntimer:123|ms', self.recv())

    def test_context_manager(self):
        fake_socket = FakeSocket()
        with monascastatsd.monasca_statsd.MonascaStatsd() as statsd:
            statsd.socket = fake_socket
            statsd.gauge('page.views', 123)
            statsd.timing('timer', 123)

        self.assertEqual('page.views:123|g\ntimer:123|ms', fake_socket.recv())

    def test_batched_buffer_autoflush(self):
        fake_socket = FakeSocket()
        with monascastatsd.monasca_statsd.MonascaStatsd() as statsd:
            statsd.socket = fake_socket
            for _ in range(51):
                statsd.increment('mycounter')
            self.assertEqual('\n'.join(['mycounter:1|c' for _ in range(50)]),
                             fake_socket.recv())

        self.assertEqual('mycounter:1|c', fake_socket.recv())


if __name__ == '__main__':
    unittest.main()
