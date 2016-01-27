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


class MetricBase(object):
    """Base class for all metric types.

    """

    def __init__(self, name, connection, dimensions):
        self._name = name
        self._connection = connection
        self._dimensions = dimensions

    def update_dimensions(self, dimensions):
        """Update the dimensions list with the default

        dimensions that were passed in on instantiation.
        """
        if self._dimensions:
            new_dimensions = self._dimensions.copy()
        else:
            new_dimensions = {}
        if dimensions:
            new_dimensions.update(dimensions)

        return new_dimensions

    def update_name(self, name):
        """Update the metric name with the metric

        base name that was passed in on instantiation.
        """
        if self._name:
            metric = self._name
            if name:
                metric = metric + "." + name
        else:
            metric = name
        return metric
