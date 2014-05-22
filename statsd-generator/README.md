# Python Monasca-statsd Generator

This test tool will create monasca-statsd metrics and send them to the monitoring agent.
To use it, you will need to install the following python libraries:
```
sudo apt-get install python-setuptools
sudo pip install monasca-statsd
```

## Usage
### To run the generator:
```
1) edit the config file (generator.conf) and set the target host, port, number of
iterations and delay (in seconds) between iterations.
2) cd to the statsd-generator directory
3) Type ./generator.py
4) The tool will send 4 different types of monasca-statsd messages to the monitoring
agent and then sleep for the duration of the delay and then will continue to the
next iteration until the number of iterations is reached.
```