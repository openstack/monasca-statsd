from metricbase import MetricBase


class Counter(MetricBase):

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
        self._connection.report(metric=self._name,
                                metric_type='c',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)

    def decrement(self, value=1, dimensions=None, sample_rate=1):
        """Decrement a counter, optionally setting a value, dimensions and a

        sample rate.

        >>> monascastatsd.decrement()
        >>> monascastatsd.decrement(2)
        """
        self._connection.report(metric=self._name,
                                metric_type='c',
                                value=-value,
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
