# (C) Copyright 2014-2016 Hewlett Packard Enterprise Development LP
# Copyright 2016 FUJITSU LIMITED
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

import six

import logging
import random
import socket

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
        self.max_buffer_size = max_buffer_size
        self._send = self._send_to_server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        self.socket.connect((host, int(port)))

    def report(self, metric, metric_type, value, dimensions, sample_rate):
        """Use this connection to report metrics.

        """
        if sample_rate == 1 or random.random() <= sample_rate:
            self._send_payload(dimensions, metric,
                               metric_type, sample_rate,
                               value)

    def _send_payload(self, dimensions, metric, metric_type,
                      sample_rate, value):

        encoded = self._create_payload(dimensions, metric,
                                       metric_type, sample_rate,
                                       value)

        self._send(encoded)

    def _create_payload(self, dimensions, metric, metric_type, sample_rate,
                        value):

        payload = [metric, ":", value, "|", metric_type]
        payload.extend(self._payload_extension_from_sample_rate(sample_rate))
        payload.extend(self._payload_extension_from_dimensions(dimensions))

        return "".join(six.moves.map(str, payload))

    @staticmethod
    def _payload_extension_from_sample_rate(sample_rate):
        if sample_rate != 1:
            return ["|@", sample_rate]
        else:
            return []

    @staticmethod
    def _payload_extension_from_dimensions(dimensions):
        if dimensions:
            return ["|#", dimensions]
        else:
            return []

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
