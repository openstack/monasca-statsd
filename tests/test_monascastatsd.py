# (C) Copyright 2014-2016 Hewlett Packard Enterprise Development LP
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
#
# Copyright (c) 2012, Datadog <info@datadoghq.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Datadog nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DATADOG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -*- coding: utf-8 -*-

"""Tests for monascastatsd.py."""

import collections
import socket
import time
import unittest

import monascastatsd as mstatsd

from unittest import mock
import six
from six.moves import range


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

    @mock.patch('monascastatsd.client.Connection')
    def test_client_set_host_port(self, connection_mock):
        mstatsd.Client(host='foo.bar', port=5213)
        connection_mock.assert_called_once_with(host='foo.bar',
                                                port=5213,
                                                max_buffer_size=50)

    @mock.patch('monascastatsd.client.Connection')
    def test_client_default_host_port(self, connection_mock):
        mstatsd.Client()
        connection_mock.assert_called_once_with(host='localhost',
                                                port=8125,
                                                max_buffer_size=50)

    def test_counter(self):
        counter = self.client.get_counter(name='page.views')

        counter.increment()
        self.assertEqual(six.b("page.views:1|c|#{'env': 'test'}"),
                         self.recv(counter))

        counter += 1
        self.assertEqual(six.b("page.views:1|c|#{'env': 'test'}"),
                         self.recv(counter))

        counter.increment(11)
        self.assertEqual(six.b("page.views:11|c|#{'env': 'test'}"),
                         self.recv(counter))

        counter += 11
        self.assertEqual(six.b("page.views:11|c|#{'env': 'test'}"),
                         self.recv(counter))

        counter.decrement()
        self.assertEqual(six.b("page.views:-1|c|#{'env': 'test'}"),
                         self.recv(counter))

        counter -= 1
        self.assertEqual(six.b("page.views:-1|c|#{'env': 'test'}"),
                         self.recv(counter))

        counter.decrement(12)
        self.assertEqual(six.b("page.views:-12|c|#{'env': 'test'}"),
                         self.recv(counter))

        counter -= 12
        self.assertEqual(six.b("page.views:-12|c|#{'env': 'test'}"),
                         self.recv(counter))

    def test_counter_with_dimensions(self):
        counter = self.client.get_counter('counter_with_dims',
                                          dimensions={'date': '10/24', 'time': '23:00'})

        counter.increment(dimensions={'country': 'canada', 'color': 'red'})

        result = self.recv(counter)
        if isinstance(result, bytes):
            result = result.decode('utf-8')

        self.assertRegexpMatches(result, "counter_with_dims:1|c|#{")
        self.assertRegexpMatches(result, "'country': 'canada'")
        self.assertRegexpMatches(result, "'date': '10/24'")
        self.assertRegexpMatches(result, "'color': 'red'")
        self.assertRegexpMatches(result, "'env': 'test'")
        self.assertRegexpMatches(result, "'time': '23:00'")

        counter += 1

        result = self.recv(counter)
        if isinstance(result, bytes):
            result = result.decode('utf-8')

        self.assertRegexpMatches(result, "counter_with_dims:1|c|#{")
        self.assertRegexpMatches(result, "'date': '10/24'")
        self.assertRegexpMatches(result, "'env': 'test'")
        self.assertRegexpMatches(result, "'time': '23:00'")

    def test_gauge(self):
        gauge = self.client.get_gauge('gauge')
        gauge.send('metric', 123.4)
        result = self.recv(gauge)
        if isinstance(result, bytes):
            result = result.decode('utf-8')

        assert result == "gauge.metric:123.4|g|#{'env': 'test'}"

    def test_gauge_with_dimensions(self):
        gauge = self.client.get_gauge('gauge')
        gauge.send('gt', 123.4,
                   dimensions={'country': 'china',
                               'age': 45,
                               'color': 'blue'})

        result = self.recv(gauge)
        if isinstance(result, bytes):
            result = result.decode('utf-8')

        self.assertRegexpMatches(result, "gauge.gt:123.4|g|#{")
        self.assertRegexpMatches(result, "'country': 'china'")
        self.assertRegexpMatches(result, "'age': 45")
        self.assertRegexpMatches(result, "'color': 'blue'")
        self.assertRegexpMatches(result, "'env': 'test'")

    def test_sample_rate(self):
        counter = self.client.get_counter('sampled_counter')
        counter.increment(sample_rate=0)
        assert not self.recv(counter)
        for _ in range(10000):
            counter.increment(sample_rate=0.3)
        self.assert_almost_equal(3000,
                                 len(self.client.connection.socket.payloads),
                                 150)
        self.assertEqual(six.b("sampled_counter:1|c|@0.3|#{'env': 'test'}"), self.recv(counter))

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
        self.assertEqual(six.b("t:123|g|#{'env': 'test'}"), self.recv(timer))

    def test_time(self):
        timer = self.client.get_timer()
        with timer.time('t'):
            time.sleep(2)
        packet = self.recv(timer)
        if isinstance(packet, bytes):
            packet = packet.decode("utf-8")

        name_value, type_, dimensions = packet.split('|')
        name, value = name_value.split(':')

        self.assertEqual('g', type_)
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
        if isinstance(packet, bytes):
            packet = packet.decode("utf-8")

        name_value, type_, dimensions = packet.split('|')
        name, value = name_value.split(':')

        self.assertEqual('g', type_)
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

        self.assertEqual(six.b("site.views:123|g|#{'env': 'test'}\n"
                               "site.timer:123|g|#{'env': 'test'}"),
                         self.recv(gauge))

    def test_context_manager(self):
        fake_socket = FakeSocket()
        with mstatsd.Connection() as conn:
            conn.socket = fake_socket
            client = mstatsd.Client(name='ContextTester', connection=conn)
            client.get_gauge('page').send('views', 123)
            client.get_timer('page').timing('timer', 12)

        self.assertEqual(six.b('ContextTester.page.views:123|g\nContextTester.page.timer:12|g'),
                         fake_socket.recv())

    def test_batched_buffer_autoflush(self):
        fake_socket = FakeSocket()
        with mstatsd.Connection() as conn:
            conn.socket = fake_socket
            client = mstatsd.Client(name='BufferedTester', connection=conn)
            counter = client.get_counter('mycounter')
            for _ in range(51):
                counter.increment()
            self.assertEqual(six.b('\n'.join(['BufferedTester.mycounter:1|c' for _ in range(50)])),
                             fake_socket.recv())

        self.assertEqual(six.b('BufferedTester.mycounter:1|c'), fake_socket.recv())

    @staticmethod
    def assert_almost_equal(a, b, delta):
        assert 0 <= abs(a - b) <= delta, "%s - %s not within %s" % (a,
                                                                    b,
                                                                    delta)


if __name__ == '__main__':
    unittest.main()
