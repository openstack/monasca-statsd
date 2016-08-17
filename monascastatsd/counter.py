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

from monascastatsd import metricbase


class Counter(metricbase.MetricBase):

    def __init__(self, name, connection, dimensions=None):
        super(self.__class__, self).__init__(name=name,
                                             connection=connection,
                                             dimensions=dimensions)

    def increment(self, value=1, dimensions=None, sample_rate=1):
        """Increment a counter, optionally setting a value, dimensions

        and a sample rate.

        >>> monascastatsd.increment()
        >>> monascastatsd.increment(12)
        """
        self._report_change(dimensions, sample_rate, value)

    def decrement(self, value=1, dimensions=None, sample_rate=1):
        """Decrement a counter, optionally setting a value, dimensions and a

        sample rate.

        >>> monascastatsd.decrement()
        >>> monascastatsd.decrement(2)
        """
        self._report_change(dimensions, sample_rate, -value)

    def _report_change(self, dimensions, sample_rate, value):
        self._connection.report(metric=self._name,
                                metric_type='c',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)

    def __add__(self, value):
        """Increment the counter with `value`

            :keyword value: The value to add to the counter
            :type value: int
        """
        self.increment(value=value)
        return self

    def __sub__(self, value):
        """Decrement the counter with `value`

            :keyword value: The value to remove from the counter
            :type value: int
        """
        self.decrement(value=value)
        return self
