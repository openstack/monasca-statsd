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

import ConfigParser
import random
import time

import monascastatsd as mstatsd

import statsd

'''The statsd generator will provide a testbed for testing

the monasca agent statsd capability with dimensions
'''


class MonascaStatsdGenerator(object):

    '''Class to generate MonascaStatsd metrics.'''

    def __init__(self, config):
        '''Constructor.'''
        print (config)
        self.num_of_iterations = int(config["iterations"])
        self.delay = int(config["delay"])
        self.host = config["host"]
        self.port = config["port"]

    def send_messages(self):
        '''Main processing for sending messages.'''
        try:
            conn = mstatsd.Connection(host=self.host, port=self.port)
            self.client = mstatsd.Client(name='statsd-generator', connection=conn)
            for index in range(1, self.num_of_iterations + 1):
                print("Starting iteration " + str(index) +
                      " of " + str(self.num_of_iterations))
                counter = self.client.get_counter('teraflops')
                counter.increment(5)
                gauge = self.client.get_gauge()
                gauge.send('num_of_teraflops',
                           random.uniform(1.0, 10.0),
                           dimensions={'origin': 'dev',
                                       'environment': 'test'})
                histogram = self.client.get_histogram('hist')
                histogram.send('file.upload.size',
                               random.randrange(1, 100),
                               dimensions={'version': '1.0'})
                set = self.client.get_set('hist')
                set.send('load_time',
                         random.randrange(1, 100),
                         dimensions={'page_name': 'mypage.html'})

                timer = self.client.get_timer('timer')

                @timer.timed('config_db_time',
                             dimensions={'db_name': 'mydb'})
                def time_db():
                    time.sleep(0.2)
                time_db()

                with timer.time('time_block'):
                    time.sleep(0.3)

                # Send some regular statsd messages
                counter = statsd.Counter('statsd_counter')
                counter += 1
                gauge = statsd.Gauge('statsd_gauge')
                gauge.send('cpu_percent',
                           random.uniform(1.0, 100.0))
                print("Completed iteration " + str(index) +
                      ".  Sleeping for " + str(self.delay) + " seconds...")
                time.sleep(self.delay)
        except Exception:
            print ("Error sending statsd messages...")
            raise


def read_config():
    '''Read in the config file.'''
    config = ConfigParser.ConfigParser()
    config.read("generator.conf")
    config_options = {}
    section = "main"
    options = config.options(section)
    for option in options:
        try:
            config_options[option] = config.get(section, option)
            if config_options[option] == -1:
                print("skip: %s" % option)
        except Exception:
            print("exception on %s!" % option)
            config_options[option] = None
    return config_options


def main():
    config = read_config()
    generator = MonascaStatsdGenerator(config)
    generator.send_messages()

if __name__ == "__main__":
    main()
