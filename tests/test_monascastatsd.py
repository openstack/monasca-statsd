# (C) Copyright 2014 Hewlett Packard Enterprise Development Company LP
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

import monascastatsd as mstatsd


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


class TestMonascaStatsd(unittest.TestCase):

    def setUp(self):
        conn = mstatsd.Connection()
        conn.socket = FakeSocket()
        self.client = mstatsd.Client(connection=conn, dimensions={'env': 'test'})

    def recv(self, metric_obj):
        return metric_obj._connection.socket.recv()

    def test_counter(self):
        counter = self.client.get_counter(name='page.views')

        counter.increment()
        self.assertEqual("page.views:1|c|#{'env': 'test'}",
                         self.recv(counter))

        counter += 1
        self.assertEqual("page.views:1|c|#{'env': 'test'}",
                         self.recv(counter))

        counter.increment(11)
        self.assertEqual("page.views:11|c|#{'env': 'test'}",
                         self.recv(counter))

        counter += 11
        self.assertEqual("page.views:11|c|#{'env': 'test'}",
                         self.recv(counter))

        counter.decrement()
        self.assertEqual("page.views:-1|c|#{'env': 'test'}",
                         self.recv(counter))

        counter -= 1
        self.assertEqual("page.views:-1|c|#{'env': 'test'}",
                         self.recv(counter))

        counter.decrement(12)
        self.assertEqual("page.views:-12|c|#{'env': 'test'}",
                         self.recv(counter))

        counter -= 12
        self.assertEqual("page.views:-12|c|#{'env': 'test'}",
                         self.recv(counter))

    def test_counter_with_dimensions(self):
        counter = self.client.get_counter('counter_with_dims',
                                          dimensions={'date': '10/24', 'time': '23:00'})

        counter.increment(dimensions={'country': 'canada', 'color': 'red'})
        self.assertEqual("counter_with_dims:1|c|#{'date': '10/24', 'color': 'red', " +
                         "'country': 'canada', 'env': 'test', 'time': '23:00'}",
                         self.recv(counter))

        counter += 1
        self.assertEqual("counter_with_dims:1|c|#{'date': '10/24', 'env': 'test', 'time': '23:00'}",
                         self.recv(counter))

    def test_set(self):
        set = self.client.get_set('set')
        set.send('metric', 123)
        assert self.recv(set) == "set.metric:123|s|#{'env': 'test'}"

    def test_gauge(self):
        gauge = self.client.get_gauge('gauge')
        gauge.send('metric', 123.4)
        assert self.recv(gauge) == "gauge.metric:123.4|g|#{'env': 'test'}"

    def test_histogram(self):
        histogram = self.client.get_histogram('histogram')

        histogram.send('metric', 123.4)
        self.assertEqual("histogram.metric:123.4|h|#{'env': 'test'}", self.recv(histogram))

    def test_gauge_with_dimensions(self):
        gauge = self.client.get_gauge('gauge')
        gauge.send('gt', 123.4,
                   dimensions={'country': 'china',
                               'age': 45,
                               'color': 'blue'})
        self.assertEqual("gauge.gt:123.4|g|#{" +
                         "'color': 'blue', " +
                         "'country': 'china', " +
                         "'age': 45, " +
                         "'env': 'test'}",
                         self.recv(gauge))

    def test_histogram_with_dimensions(self):
        histogram = self.client.get_histogram('my_hist')
        histogram.send('h', 1, dimensions={'color': 'red'})
        self.assertEqual("my_hist.h:1|h|#{'color': 'red', 'env': 'test'}", self.recv(histogram))

    def test_sample_rate(self):
        counter = self.client.get_counter('sampled_counter')
        counter.increment(sample_rate=0)
        assert not self.recv(counter)
        for _ in range(10000):
            counter.increment(sample_rate=0.3)
        self.assert_almost_equal(3000,
                                 len(self.client.connection.socket.payloads),
                                 150)
        self.assertEqual("sampled_counter:1|c|@0.3|#{'env': 'test'}", self.recv(counter))

    def test_samples_with_dimensions(self):
        gauge = self.client.get_gauge()
        for _ in range(100):
            gauge.send('gst',
                       23,
                       dimensions={'status': 'sampled'},
                       sample_rate=0.9)

    def test_timing(self):
        timer = self.client.get_timer()
        timer.timing('t', 123)
        self.assertEqual("t:123|ms|#{'env': 'test'}", self.recv(timer))

    def test_time(self):
        timer = self.client.get_timer()
        with timer.time('t'):
            time.sleep(2)
        packet = self.recv(timer)
        name_value, type_, dimensions = packet.split('|')
        name, value = name_value.split(':')

        self.assertEqual('ms', type_)
        self.assertEqual('t', name)
        self.assert_almost_equal(2.0, float(value), 0.1)
        self.assertEqual("{'env': 'test'}", dimensions.lstrip('#'))

    def test_timed(self):
        timer = self.client.get_timer()

        @timer.timed('timed.test')
        def func(a, b, c=1, d=1):
            """docstring."""
            time.sleep(0.5)
            return (a, b, c, d)

        self.assertEqual('func', func.__name__)
        self.assertEqual('docstring.', func.__doc__)

        result = func(1, 2, d=3)
        # Assert it handles args and kwargs correctly.
        self.assertEqual(result, (1, 2, 1, 3))

        packet = self.recv(timer)
        name_value, type_, dimensions = packet.split('|')
        name, value = name_value.split(':')

        self.assertEqual('ms', type_)
        self.assertEqual('timed.test', name)
        self.assert_almost_equal(0.5, float(value), 0.1)
        self.assertEqual("{'env': 'test'}", dimensions.lstrip('#'))

    def test_socket_error(self):
        self.client.connection.socket = BrokenSocket()
        self.client.get_gauge().send('no error', 1)
        assert True, 'success'
        self.client.connection.socket = FakeSocket()

    def test_batched(self):
        self.client.connection.open_buffer()
        gauge = self.client.get_gauge('site')
        gauge.send('views', 123)
        timer = self.client.get_timer('site')
        timer.timing('timer', 123)
        self.client.connection.close_buffer()

        self.assertEqual("site.views:123|g|#{'env': 'test'}\nsite.timer:123|ms|#{'env': 'test'}",
                         self.recv(gauge))

    def test_context_manager(self):
        fake_socket = FakeSocket()
        with mstatsd.Connection() as conn:
            conn.socket = fake_socket
            client = mstatsd.Client(name='ContextTester', connection=conn)
            client.get_gauge('page').send('views', 123)
            client.get_timer('page').timing('timer', 12)

        self.assertEqual('ContextTester.page.views:123|g\nContextTester.page.timer:12|ms',
                         fake_socket.recv())

    def test_batched_buffer_autoflush(self):
        fake_socket = FakeSocket()
        with mstatsd.Connection() as conn:
            conn.socket = fake_socket
            client = mstatsd.Client(name='BufferedTester', connection=conn)
            counter = client.get_counter('mycounter')
            for _ in range(51):
                counter.increment()
            self.assertEqual('\n'.join(['BufferedTester.mycounter:1|c' for _ in range(50)]),
                             fake_socket.recv())

        self.assertEqual('BufferedTester.mycounter:1|c', fake_socket.recv())

    @staticmethod
    def assert_almost_equal(a, b, delta):
        assert 0 <= abs(a - b) <= delta, "%s - %s not within %s" % (a,
                                                                    b,
                                                                    delta)

if __name__ == '__main__':
    unittest.main()
