from metricbase import MetricBase


class Set(MetricBase):

    def __init__(self, connection, name=None, dimensions=None):
        super(self.__class__, self).__init__(name=name,
                                             connection=connection,
                                             dimensions=dimensions)

    def send(self, name, value, dimensions=None, sample_rate=1):
        """Sample a set value.

        >>> monascastatsd.set('visitors.uniques', 999)
        """

        self._connection.report(metric=self.update_name(name),
                                metric_type='s',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)
