# ----------------------------------------------------------------- #
#           The HMM-Based Speech Synthesis System (HTS)             #
#           developed by HTS Working Group                          #
#           http://hts.sp.nitech.ac.jp/                             #
# ----------------------------------------------------------------- #
#                                                                   #
#  Copyright (c) 2014-2016  Nagoya Institute of Technology          #
#                           Department of Computer Science          #
#                                                                   #
# All rights reserved.                                              #
#                                                                   #
# Redistribution and use in source and binary forms, with or        #
# without modification, are permitted provided that the following   #
# conditions are met:                                               #
#                                                                   #
# - Redistributions of source code must retain the above copyright  #
#   notice, this list of conditions and the following disclaimer.   #
# - Redistributions in binary form must reproduce the above         #
#   copyright notice, this list of conditions and the following     #
#   disclaimer in the documentation and/or other materials provided #
#   with the distribution.                                          #
# - Neither the name of the HTS working group nor the names of its  #
#   contributors may be used to endorse or promote products derived #
#   from this software without specific prior written permission.   #
#                                                                   #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND            #
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,       #
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF          #
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE          #
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS #
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,          #
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED   #
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,     #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON #
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,   #
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY    #
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           #
# POSSIBILITY OF SUCH DAMAGE.                                       #
# ----------------------------------------------------------------- #

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import numpy
import os
import re
import struct
import ConfigParser

from six.moves import xrange
import tensorflow as tf


class InputOutputPairs(object):

    def __init__(self, inputs, outputs, seed=None):
        assert inputs.shape[0] == outputs.shape[0]

        self._inputs = inputs.astype(numpy.float32)
        self._outputs = outputs.astype(numpy.float32)
        self._num_examples = inputs.shape[0]
        self._num_epochs = 0

        self._index = 0
        self._rng = numpy.random.RandomState(seed)

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def num_epochs(self):
        return self._num_epochs

    def get_pairs(self, batch_size, shuffle=True):
        start = self._index
        end = self._index + batch_size

        if end > self._num_examples:
            if shuffle:
                random_indices = numpy.arange(self._num_examples)
                self._rng.shuffle(random_indices)
                self._inputs = self._inputs[random_indices]
                self._outputs = self._outputs[random_indices]

            start = 0
            end = batch_size
            self._num_epochs += 1

        self._index = end
        return self._inputs[start:end], self._outputs[start:end]


def get_filenames(script_file):
    input_filenames = []
    output_filenames = []
    for filenames in open(script_file, 'r'):
        if re.search(' ', filenames) is None:
            input_filenames.append(filenames.rstrip())
            output_filenames.append(None)
        else:
            input_filename, output_filename = filenames.split(' ', 1)
            input_filenames.append(input_filename.rstrip())
            output_filenames.append(output_filename.rstrip())

    return input_filenames, output_filenames


def read_data_from_queue(
        script_file, num_dimensions, num_epochs, batch_size, seed,
        min_after_dequeue, num_threads):
    assert seed is not None

    with tf.device('/cpu:0'):
        if script_file is None or not os.path.isfile(script_file):
            raise IOError('No such file %s' % script_file)

        input_filenames, output_filenames = get_filenames(script_file)

        input_filename_queue = tf.train.string_input_producer(
            input_filenames, num_epochs=num_epochs,
            shuffle=True, seed=seed, capacity=1000)
        output_filename_queue = tf.train.string_input_producer(
            output_filenames, num_epochs=num_epochs,
            shuffle=True, seed=seed, capacity=1000)

        def get_example(filename_queue, num_dimensions):
            reader = tf.FixedLengthRecordReader(4 * num_dimensions)
            _, value = reader.read(filename_queue)
            return tf.decode_raw(value, tf.float32, little_endian=True)

        num_input_dimensions, num_output_dimensions = num_dimensions
        input_example = tf.slice(
            get_example(input_filename_queue, num_input_dimensions),
            [0], [num_input_dimensions])
        output_example = tf.slice(
            get_example(output_filename_queue, num_output_dimensions),
            [0], [num_output_dimensions])

        size = 0
        for filename in input_filenames:
            stat = os.stat(filename)
            size = size + stat.st_size
            num_examples = size // (4 * num_input_dimensions)

        safety_margin = 1
        capacity = (min_after_dequeue +
                    (num_threads + safety_margin) * batch_size)

        inputs, outputs = tf.train.shuffle_batch(
            [input_example, output_example], batch_size, capacity,
            min_after_dequeue, num_threads=num_threads, seed=seed,
            allow_smaller_final_batch=False)

    return [inputs, outputs], num_examples


def read_data_from_script(
        script_file, num_dimensions, shuffle=True, seed=None):
    with tf.device('/cpu:0'):
        if script_file is None or not os.path.isfile(script_file):
            raise IOError('No such file %s' % script_file)

        input_data = []
        output_data = []
        for filenames in open(script_file, 'r'):
            input_filename, output_filename = filenames.split(' ', 1)
            with open(input_filename.rstrip(), 'rb') as f:
                packed_data = f.read(4)
                while packed_data != '':
                    input_data.extend(struct.unpack('f', packed_data))
                    packed_data = f.read(4)
            with open(output_filename.rstrip(), 'rb') as f:
                packed_data = f.read(4)
                while packed_data != '':
                    output_data.extend(struct.unpack('f', packed_data))
                    packed_data = f.read(4)

        num_input_dimensions, num_output_dimensions = num_dimensions
        inputs = numpy.reshape(input_data, [-1, num_input_dimensions])
        outputs = numpy.reshape(output_data, [-1, num_output_dimensions])
        assert len(inputs) == len(outputs)

        num_examples = len(inputs)
        if shuffle:
            rng = numpy.random.RandomState(seed)
            random_indices = numpy.arange(num_examples)
            rng.shuffle(random_indices)
            inputs = inputs[random_indices]
            outputs = outputs[random_indices]

    return InputOutputPairs(inputs, outputs, seed=seed), num_examples


def read_data_from_file(filenames, num_dimensions):
    input_filename, output_filename = filenames
    num_input_dimensions, num_output_dimensions = num_dimensions

    with tf.device('/cpu:0'):
        inputs = read_data(input_filename, num_input_dimensions)
        num_examples = len(inputs)

        if output_filename is None:
            outputs = numpy.zeros([num_examples, num_output_dimensions])
        else:
            outputs = read_data(output_filename, num_output_dimensions)

    return InputOutputPairs(inputs, outputs), num_examples


def batched_data(num_dimensions, batch_size):
    num_input_dimensions, num_output_dimensions = num_dimensions

    inputs = tf.placeholder(
        tf.float32, shape=[batch_size, num_input_dimensions])
    outputs = tf.placeholder(
        tf.float32, shape=[batch_size, num_output_dimensions])

    return inputs, outputs


def read_data(filename, num_dimensions=None):
    if filename is None or not os.path.isfile(filename):
        raise IOError('No such file %s' % filename)

    data = []
    mode = 'rb'
    with open(filename, mode) as f:
        packed_data = f.read(4)
        while packed_data != '':
            data.extend(struct.unpack('f', packed_data))
            packed_data = f.read(4)

    if num_dimensions is not None:
        data = numpy.reshape(data, [-1, num_dimensions])

    return numpy.asarray(data, dtype=numpy.float32)


def write_data(filename, data, append=False):
    mode = 'ab' if append else 'wb'
    with open(filename, mode) as f:
        for row in data:
            for elem in row:
                f.write(struct.pack('f', elem))


def load_config(config_file, verbose=True):
    config_parser = ConfigParser.SafeConfigParser()
    config_parser.read(config_file)

    config = {}
    for section in config_parser.sections():
        for option in config_parser.options(section):
            config[option] = config_parser.get(section, option)

            list_pattern = re.compile('^\[.+\]$')
            if list_pattern.search(config[option]):
                config[option] = json.loads(config[option])
                continue

            int_pattern = re.compile('^\d+$')
            if int_pattern.search(config[option]):
                config[option] = int(config[option])
                continue

            float_pattern = re.compile('^\d+\.\d+$')
            if float_pattern.search(config[option]):
                config[option] = float(config[option])
                continue

    if verbose:
        print('Configuration Parameters[%d]' % len(config))
        print('              %-25s %20s' % ('Parameter', 'Value'))
        for key in sorted(config.keys()):
            print('              %-25s %20s' % (key, str(config[key])))
        print()

    config['num_io_units'] = [
        config['num_input_units'],
        config['num_output_units']]

    return config
