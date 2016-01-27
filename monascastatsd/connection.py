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

import logging
import random
import socket

try:
    import itertools
except ImportError:
    imap = map

logging.basicConfig()
log = logging.getLogger(__name__)


class Connection(object):

    def __init__(self, host='localhost', port=8125, max_buffer_size=50):
        """Initialize a Connection object.

        >>> monascastatsd = MonascaStatsd()

        :name: the name for this client.  Everything sent by this client
            will be prefixed by name
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
        """Open a buffer to send a batch of metrics in one packet.

        """
        self.max_buffer_size = max_buffer_size
        self.buffer = []
        self._send = self._send_to_buffer

    def close_buffer(self):
        """Flush the buffer and switch back to single metric packets.

        """
        self._send = self._send_to_server
        self._flush_buffer()

    def connect(self, host, port):
        """Connect to the monascastatsd server on the given host and port.

        """
        self._host = host
        self._port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self._host, self._port))

    def report(self, metric, metric_type, value, dimensions, sample_rate):
        """Use this connection to report metrics.

        """
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
