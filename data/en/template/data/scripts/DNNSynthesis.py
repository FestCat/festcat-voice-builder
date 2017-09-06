#!/usr/bin/env python
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

import argparse
import datetime
import glob
import numpy
import os
import sys
import time

from six.moves import xrange
import tensorflow as tf

import DNNDataIO
import DNNDefine


parser = argparse.ArgumentParser()
parser.add_argument('-z', metavar='f', dest='variance', type=str, default=None,
                    help='set variance used for error calculation')
parser.add_argument('-C', metavar='cf', dest='config', type=str, required=True,
                    help='set config file to cf')
parser.add_argument('-H', metavar='dir', dest='model_dir', type=str, required=True,
                    help='set directory to load a model')
parser.add_argument('-M', metavar='dir', dest='gen_dir', type=str, default='.',
                    help='set directory to write outputs')
parser.add_argument('-S', metavar='f', dest='script', type=str, required=True,
                    help='set generation script file to f')
parser.add_argument('-X', metavar='ext', dest='extension', type=str, default='ffo',
                    help='set output file extension')
args = parser.parse_args()


def print_time(message):
    date = datetime.datetime.today().strftime('%x %X')
    print(message, 'at', date)


def format_duration(duration):
    if duration >= 1000:
        return '%.1f hour' % (duration / 3600)
    elif duration >= 100:
        return '%.1f min' % (duration / 60)
    else:
        return '%.2f sec' % (duration)


def format_num_parameters(num_parameters):
    if num_parameters >= 1e+6:
        return '%.1f M' % (num_parameters / 1e+6)
    elif num_parameters >= 1e+3:
        return '%.1f k' % (num_parameters / 1e+3)
    else:
        return num_parameters


def fill_feed_dict(
        data_set, keep_prob, placeholders, batch_size, shuffle=True):
    inputs_pl, outputs_pl, keep_prob_pl = placeholders
    inputs_feed, outputs_feed = data_set.get_pairs(batch_size, shuffle)
    feed_dict = {
        inputs_pl: inputs_feed,
        outputs_pl: outputs_feed,
        keep_prob_pl: keep_prob
    }
    return feed_dict


def forward(config, model, stddev):
    with tf.Graph().as_default():
        inputs, outputs = DNNDataIO.batched_data(config['num_io_units'], 1)
        keep_prob = tf.placeholder(tf.float32)

        predicted_outputs, _ = DNNDefine.inference(
            inputs,
            config['num_io_units'],
            config['num_hidden_units'],
            config['hidden_activation'],
            'linear',
            keep_prob)

        num_parameters = DNNDefine.get_num_parameters()
        print('Number of parameters')
        print(' ', format_num_parameters(num_parameters))
        print('')

        cost_op = DNNDefine.cost(predicted_outputs, outputs, stddev)

        init_op = tf.group(
            tf.global_variables_initializer(),
            tf.local_variables_initializer())

        saver = tf.train.Saver()

        sess = tf.Session(config=tf.ConfigProto(
            intra_op_parallelism_threads=config['num_threads']))

        sess.run(init_op)

        saver.restore(sess, model)

        input_filenames, output_filenames = DNNDataIO.get_filenames(
            args.script)

        print_time('Start forwarding')
        for i in xrange(len(input_filenames)):
            print('  Processing %s' % input_filenames[i])
            forward_data, num_examples = DNNDataIO.read_data_from_file(
                [input_filenames[i], output_filenames[i]],
                config['num_io_units'])

            basename = os.path.splitext(
                os.path.basename(input_filenames[i]))[0]
            predict_filename = os.path.join(args.gen_dir, basename)
            if args.extension != '':
                predict_filename += '.' + args.extension

            total_cost = 0.0
            start_time = time.time()

            for j in xrange(num_examples):
                feed_dict = fill_feed_dict(
                    forward_data, 1.0,
                    [inputs, outputs, keep_prob], 1, shuffle=False)

                predicts, value = sess.run(
                    [predicted_outputs, cost_op], feed_dict=feed_dict)

                total_cost += value

                append = False if j == 0 else True
                DNNDataIO.write_data(predict_filename, predicts, append)

            if output_filenames[i] is not None:
                duration = format_duration(time.time() - start_time)
                print('')
                print('    Evaluation')
                print('      cost = %e (%s)' %
                      (total_cost / num_examples, duration))
                print('')

        sess.close()

    print_time('End forwarding')
    print()


def main(_):
    config = DNNDataIO.load_config(args.config)

    if not os.path.exists(args.gen_dir):
        os.mkdir(args.gen_dir)

    model = os.path.join(args.model_dir, 'model.ckpt')
    if config['restore_ckpt'] > 0:
        model = '-'.join([model, str(config['restore_ckpt'])])
    files = glob.glob("%s*" % model)
    if len(files) == 0:
        sys.exit('  ERROR  main: No such file %s' % model)

    if args.variance is None:
        stddev = numpy.ones(
            config['num_output_units'], dtype=numpy.float32)
    else:
        variance = DNNDataIO.read_data(args.variance)
        stddev = numpy.sqrt(variance)

    forward(config, model, stddev)


if __name__ == '__main__':
    tf.app.run()
