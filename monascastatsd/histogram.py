from metricbase import MetricBase


class Histogram(MetricBase):

    def __init__(self, connection, name=None, dimensions=None):
        super(self.__class__, self).__init__(name=name,
                                             connection=connection,
                                             dimensions=dimensions)

    def send(self, name, value, dimensions=None, sample_rate=1):
        """Sample a histogram value, optionally setting dimensions and a

        sample rate.

        >>> monascastatsd.histogram('uploaded.file.size', 1445)
        >>> monascastatsd.histogram('album.photo.count', 26,
        >>>                    dimensions={"gender": "female"})
        """
        self._connection.report(metric=self.update_name(name),
                                metric_type='h',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)
