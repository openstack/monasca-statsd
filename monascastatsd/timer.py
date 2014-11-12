import contextlib
import functools
import time

from metricbase import MetricBase


class Timer(MetricBase):

    def __init__(self, connection, name=None, dimensions=None):
        super(self.__class__, self).__init__(name=name,
                                             connection=connection,
                                             dimensions=dimensions)

    def timing(self, name, value, dimensions=None, sample_rate=1):
        """Record a timing, optionally setting dimensions and a sample rate.

        >>> monascastatsd.timing("query.response.time", 1234)
        """
        self._connection.report(metric=self.update_name(name),
                                metric_type='ms',
                                value=value,
                                dimensions=self.update_dimensions(dimensions),
                                sample_rate=sample_rate)

    def timed(self, name, dimensions=None, sample_rate=1):
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
                self.timing(name,
                            time.time() - start,
                            dimensions=dimensions,
                            sample_rate=sample_rate)
                return result
            wrapped.__name__ = func.__name__
            wrapped.__doc__ = func.__doc__
            wrapped.__dict__.update(func.__dict__)
            return wrapped
        return wrapper

    @contextlib.contextmanager
    def time(self, name, dimensions=None, sample_rate=1):
        """Time a block of code, optionally setting dimensions and a sample rate.

        try:
            with monascastatsd.time("query.response.time"):
                Do something...
        except Exception:
            Log something...
        """

        start_time = time.time()
        yield
        end_time = time.time()
        self.timing(name, end_time - start_time, dimensions, sample_rate)
