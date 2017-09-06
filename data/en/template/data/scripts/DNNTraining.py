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
import numpy
import os
import time
import traceback

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
                    help='set directory to save trained models')
parser.add_argument('-N', metavar='f', dest='valid_script', type=str, default=None,
                    help='set validation script file to f')
parser.add_argument('-S', metavar='f', dest='script', type=str, required=True,
                    help='set training script file to f')
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


def train_using_queue(config, model, stddev):
    with tf.Graph().as_default():
        print('Preparing to read training data...', end='')
        train_data, num_train_examples = DNNDataIO.read_data_from_queue(
            args.script,
            config['num_io_units'],
            config['num_epochs'],
            config['batch_size'],
            config['random_seed'],
            config['queue_size'],
            2)
        print(' %d examples will be fed' % num_train_examples)

        if args.valid_script is None:
            valid_data, num_valid_examples = [None, 0]
        else:
            print('Preparing to read training data...', end='')
            valid_data, num_valid_examples = DNNDataIO.read_data_from_queue(
                args.valid_script,
                config['num_io_units'],
                None,
                config['batch_size'],
                config['random_seed'],
                config['queue_size'],
                config['num_threads_for_queue'])
            print(' %d examples will be fed' % num_valid_examples)
        print('')

        train_inputs, train_outputs = train_data
        if num_valid_examples > 0:
            valid_inputs, valid_outputs = valid_data

        predicted_train_outputs, params = DNNDefine.inference(
            train_inputs,
            config['num_io_units'],
            config['num_hidden_units'],
            config['hidden_activation'],
            config['output_activation'],
            config['keep_prob'],
            seed=config['random_seed'])

        if num_valid_examples > 0:
            predicted_valid_outputs, _ = DNNDefine.inference(
                valid_inputs,
                config['num_io_units'],
                config['num_hidden_units'],
                config['hidden_activation'],
                config['output_activation'],
                1.0,
                given_params=params)

        num_parameters = DNNDefine.get_num_parameters()
        print('Number of parameters')
        print(' ', format_num_parameters(num_parameters))
        print('')

        train_cost_op = DNNDefine.cost(
            predicted_train_outputs, train_outputs, stddev)
        if num_valid_examples > 0:
            valid_cost_op = DNNDefine.cost(
                predicted_valid_outputs, valid_outputs, stddev)

        train_op = DNNDefine.training(
            train_cost_op,
            config['optimizer'],
            config['learning_rate'])

        init_op = tf.group(
            tf.global_variables_initializer(),
            tf.local_variables_initializer())

        saver = tf.train.Saver(max_to_keep=config['num_models_to_keep'])

        sess = tf.Session(config=tf.ConfigProto(
            intra_op_parallelism_threads=config['num_threads']))

        sess.run(init_op)

        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)

        print_time('Start network training')
        try:
            total_cost = 0.0
            start_time = time.time()

            step = 1
            while not coord.should_stop():
                _, value = sess.run([train_op, train_cost_op])
                total_cost += value

                if step % config['log_interval'] == 0:
                    avg_cost = total_cost / config['log_interval']
                    duration = format_duration(time.time() - start_time)
                    print('  Step %7d: cost = %e (%s)' %
                          (step, avg_cost, duration))
                    total_cost = 0.0
                    start_time = time.time()

                if step % config['save_interval'] == 0:
                    saver.save(sess, model, global_step=step)

                    num_steps = num_valid_examples // config['batch_size']
                    if num_steps > 0:
                        cost = 0.0
                        for _ in xrange(num_steps):
                            value = sess.run(valid_cost_op)
                            cost += value

                        avg_cost = cost / num_steps
                        duration = format_duration(time.time() - start_time)
                        print('')
                        print('    Evaluation')
                        print('      validation cost = %e (%s)' %
                              (avg_cost, duration))
                        print('')
                        start_time = time.time()

                step += 1
        except tf.errors.OutOfRangeError:
            saver.save(sess, model)
        finally:
            coord.request_stop()

        coord.join(threads)
        sess.close()

    print_time('End network training')
    print()


def train(config, model, stddev):
    with tf.Graph().as_default():
        print('Reading training data...', end='')
        train_data, num_train_examples = DNNDataIO.read_data_from_script(
            args.script,
            config['num_io_units'],
            shuffle=True,
            seed=config['random_seed'])
        print(' %d examples have been loaded' % num_train_examples)

        if args.valid_script is None:
            valid_data, num_valid_examples = [None, 0]
        else:
            print('Reading validation data...', end='')
            valid_data, num_valid_examples = DNNDataIO.read_data_from_script(
                args.valid_script,
                config['num_io_units'],
                shuffle=False)
            print(' %d examples have been loaded' % num_valid_examples)
        print('')

        inputs, outputs = DNNDataIO.batched_data(
            config['num_io_units'], config['batch_size'])
        keep_prob = tf.placeholder(
            tf.float32)

        predicted_outputs, _ = DNNDefine.inference(
            inputs,
            config['num_io_units'],
            config['num_hidden_units'],
            config['hidden_activation'],
            config['output_activation'],
            keep_prob,
            seed=config['random_seed'])

        num_parameters = DNNDefine.get_num_parameters()
        print('Number of parameters')
        print(' ', format_num_parameters(num_parameters))
        print('')

        cost_op = DNNDefine.cost(predicted_outputs, outputs, stddev)

        train_op = DNNDefine.training(
            cost_op,
            config['optimizer'],
            config['learning_rate'])

        init_op = tf.group(
            tf.global_variables_initializer(),
            tf.local_variables_initializer())

        saver = tf.train.Saver(max_to_keep=config['num_models_to_keep'])

        sess = tf.Session(config=tf.ConfigProto(
            intra_op_parallelism_threads=config['num_threads']))
        sess.run(init_op)

        print_time('Start network training')
        try:
            total_cost = 0.0
            start_time = time.time()

            step = 1
            while True:
                feed_dict = fill_feed_dict(
                    train_data, config['keep_prob'],
                    [inputs, outputs, keep_prob],
                    config['batch_size'])

                if train_data.num_epochs >= config['num_epochs']:
                    saver.save(sess, model)
                    break

                _, value = sess.run([train_op, cost_op], feed_dict=feed_dict)
                total_cost += value

                if step % config['log_interval'] == 0:
                    avg_cost = total_cost / config['log_interval']
                    duration = format_duration(time.time() - start_time)
                    print('  Step %7d: cost = %e (%s)' %
                          (step, avg_cost, duration))
                    total_cost = 0.0
                    start_time = time.time()

                if step % config['save_interval'] == 0:
                    saver.save(sess, model, global_step=step)

                    num_steps = num_valid_examples // config['batch_size']
                    if num_steps > 0:
                        cost = 0.0
                        for _ in xrange(num_steps):
                            feed_dict = fill_feed_dict(
                                valid_data, 1.0,
                                [inputs, outputs, keep_prob],
                                config['batch_size'],
                                shuffle=False)
                            value = sess.run(cost_op, feed_dict=feed_dict)
                            cost += value

                        avg_cost = cost / num_steps
                        duration = format_duration(time.time() - start_time)
                        print('')
                        print('    Evaluation')
                        print('      validation cost = %e (%s)' %
                              (avg_cost, duration))
                        print('')
                        start_time = time.time()

                step += 1
        except:
            traceback.print_exc()

        sess.close()

    print_time('End network training')
    print()


def main(_):
    config = DNNDataIO.load_config(args.config)

    if not os.path.exists(args.model_dir):
        os.mkdir(args.model_dir)
    model = os.path.join(args.model_dir, 'model.ckpt')

    if args.variance is None:
        stddev = numpy.ones(
            config['num_output_dimensions'], dtype=numpy.float32)
    else:
        variance = DNNDataIO.read_data(args.variance)
        stddev = numpy.sqrt(variance)

    if config['use_queue'] > 0:
        train_using_queue(config, model, stddev)
    else:
        train(config, model, stddev)


if __name__ == '__main__':
    tf.app.run()
