from metricbase import MetricBase


class Gauge(MetricBase):

    def __init__(self, connection, name=None, dimensions=None):
        super(self.__class__, self).__init__(name=name,
                                             connection=connection,
                                             dimensions=dimensions)

    def send(self, name, value, dimensions=None, sample_rate=1):
        """Record the value of a gauge, optionally setting a list of

        dimensions and a sample rate.

        >>> monascastatsd.gauge('users.online', 123)
        >>> monascastatsd.gauge('active.connections', 1001,
        >>>                 dimensions={"protocol": "http"})
        """
        self._connection.report(metric=self.update_name(name),
                                metric_type='g',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)
