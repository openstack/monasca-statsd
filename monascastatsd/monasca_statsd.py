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

"""Monasca-Statsd is a Python client for Statsd that adds dimensions.
"""

import functools
import logging
import random
import socket
import time

try:
    import itertools
except ImportError:
    imap = map


log = logging.getLogger(__name__)


class MonascaStatsd(object):

    def __init__(self, host='localhost', port=8125, max_buffer_size=50):
        """Initialize a MonascaStatsd object.

        >>> monascastatsd = MonascaStatsd()

        :param host: the host of the MonascaStatsd server.
        :param port: the port of the MonascaStatsd server.
        :param max_buffer_size: Maximum number of metric to buffer before
         sending to the server if sending metrics in batch
        """
        self._host = None
        self._port = None
        self.socket = None
        self.max_buffer_size = max_buffer_size
        self._send = self._send_to_server
        self.connect(host, port)
        self.encoding = 'utf-8'

    def __enter__(self):
        self.open_buffer(self.max_buffer_size)
        return self

    def __exit__(self, the_type, value, traceback):
        self.close_buffer()

    def open_buffer(self, max_buffer_size=50):
        '''Open a buffer to send a batch of metrics in one packet

        You can also use this as a context manager.

        >>> with DogStatsd() as batch:
        >>>     batch.gauge('users.online', 123)
        >>>     batch.gauge('active.connections', 1001)

        '''
        self.max_buffer_size = max_buffer_size
        self.buffer = []
        self._send = self._send_to_buffer

    def close_buffer(self):
        '''Flush the buffer and switch back to single metric packets.'''
        self._send = self._send_to_server
        self._flush_buffer()

    def connect(self, host, port):
        """Connect to the monascastatsd server on the given host and port."""
        self._host = host
        self._port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self._host, self._port))

    def gauge(self, metric, value, dimensions=None, sample_rate=1):
        """Record the value of a gauge, optionally setting a list of

        dimensions and a sample rate.

        >>> monascastatsd.gauge('users.online', 123)
        >>> monascastatsd.gauge('active.connections', 1001,
        >>>                 dimensions={"protocol": "http"})
        """
        return self._report(metric, 'g', value, dimensions, sample_rate)

    def increment(self, metric, value=1, dimensions=None, sample_rate=1):
        """Increment a counter, optionally setting a value, dimensions

        and a sample rate.

        >>> monascastatsd.increment('page.views')
        >>> monascastatsd.increment('files.transferred', 124)
        """
        self._report(metric, 'c', value, dimensions, sample_rate)

    def decrement(self, metric, value=1, dimensions=None, sample_rate=1):
        """Decrement a counter, optionally setting a value, dimensions and a

        sample rate.

        >>> monascastatsd.decrement('files.remaining')
        >>> monascastatsd.decrement('active.connections', 2)
        """
        self._report(metric, 'c', -value, dimensions, sample_rate)

    def histogram(self, metric, value, dimensions=None, sample_rate=1):
        """Sample a histogram value, optionally setting dimensions and a

        sample rate.

        >>> monascastatsd.histogram('uploaded.file.size', 1445)
        >>> monascastatsd.histogram('album.photo.count', 26,
        >>>                    dimensions={"gender": "female"})
        """
        self._report(metric, 'h', value, dimensions, sample_rate)

    def timing(self, metric, value, dimensions=None, sample_rate=1):
        """Record a timing, optionally setting dimensions and a sample rate.

        >>> monascastatsd.timing("query.response.time", 1234)
        """
        self._report(metric, 'ms', value, dimensions, sample_rate)

    def timed(self, metric, dimensions=None, sample_rate=1):
        """A decorator that will measure the distribution of a function's

        run time.  Optionally specify a list of tag or a sample rate.
        ::

            @monascastatsd.timed('user.query.time', sample_rate=0.5)
            def get_user(user_id):
                # Do what you need to ...
                pass

            # Is equivalent to ...
            start = time.time()
            try:
                get_user(user_id)
            finally:
                monascastatsd.timing('user.query.time', time.time() - start)
        """
        def wrapper(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                self.timing(metric,
                            time.time() - start,
                            dimensions=dimensions,
                            sample_rate=sample_rate)
                return result
            wrapped.__name__ = func.__name__
            wrapped.__doc__ = func.__doc__
            wrapped.__dict__.update(func.__dict__)
            return wrapped
        return wrapper

    def set(self, metric, value, dimensions=None, sample_rate=1):
        """Sample a set value.

        >>> monascastatsd.set('visitors.uniques', 999)
        """

        self._report(metric, 's', value, dimensions, sample_rate)

    def _report(self, metric, metric_type, value, dimensions, sample_rate):
        if sample_rate != 1 and random.random() > sample_rate:
            return

        payload = [metric, ":", value, "|", metric_type]
        if sample_rate != 1:
            payload.extend(["|@", sample_rate])
        if dimensions:
            payload.extend(["|#"])
            payload.append(dimensions)

        encoded = "".join(itertools.imap(str, payload))
        self._send(encoded)

    def _send_to_server(self, packet):
        try:
            self.socket.send(packet.encode(self.encoding))
        except socket.error:
            log.exception("Error submitting metric")

    def _send_to_buffer(self, packet):
        self.buffer.append(packet)
        if len(self.buffer) >= self.max_buffer_size:
            self._flush_buffer()

    def _flush_buffer(self):
        self._send_to_server("\n".join(self.buffer))
        self.buffer = []

monascastatsd = MonascaStatsd()
