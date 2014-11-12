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
