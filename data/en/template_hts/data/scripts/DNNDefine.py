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

import math

from six.moves import xrange
import tensorflow as tf


def get_activation_function(string):
    word = string.lower()
    if word == 'linear':
        return tf.identity
    elif word == 'sigmoid':
        return tf.nn.sigmoid
    elif word == 'tanh':
        return tf.nn.tanh
    elif word == 'relu':
        return tf.nn.relu
    else:
        raise NotImplementedError


def get_optimizer(string, learning_rate):
    word = string.lower()
    if word == 'sgd':
        return tf.train.GradientDescentOptimizer(learning_rate)
    elif word == 'momentum':
        return tf.train.MomentumOptimizer(learning_rate, 0.9)
    elif word == 'adagrad':
        return tf.train.AdagradOptimizer(learning_rate)
    elif word == 'adadelta':
        return tf.train.AdadeltaOptimizer(learning_rate)
    elif word == 'adam':
        return tf.train.AdamOptimizer(learning_rate)
    elif word == 'rmsprop':
        return tf.train.RMSPropOptimizer(learning_rate)
    else:
        raise NotImplementedError


def get_num_parameters():
    total_params = 0
    for variable in tf.trainable_variables():
        num_params = 1
        for dimension in variable.get_shape():
            num_params *= dimension.value
        total_params += num_params
    return total_params


def inference(inputs, num_io_units, num_hidden_units,
              hidden_activation, output_activation, keep_prob,
              seed=None, given_params=None):
    tf.set_random_seed(seed)

    num_input_units, num_output_units = num_io_units
    hidden_activation_function = get_activation_function(hidden_activation)
    output_activation_function = get_activation_function(output_activation)

    param_num = 0
    params = []

    hidden_outputs = None
    num_hidden_layers = len(num_hidden_units)

    for i in xrange(num_hidden_layers):
        with tf.name_scope('hidden' + str(i)):
            if i == 0:
                hidden_inputs = inputs
                num_prev_hidden_units = num_input_units
            else:
                hidden_inputs = hidden_outputs
                num_prev_hidden_units = num_hidden_units[i - 1]

            if given_params is None:
                weights = tf.Variable(
                    tf.truncated_normal(
                        [num_prev_hidden_units, num_hidden_units[i]],
                        stddev=1.0 / math.sqrt(float(num_prev_hidden_units))),
                    name='weights')
                biases = tf.Variable(
                    tf.zeros([num_hidden_units[i]]),
                    name='biases')
                params.extend([weights, biases])
            else:
                weights = given_params[param_num]
                param_num += 1
                biases = given_params[param_num]
                param_num += 1

            hidden_outputs = hidden_activation_function(
                tf.matmul(hidden_inputs, weights) + biases)

            hidden_outputs = tf.nn.dropout(hidden_outputs, keep_prob)

    with tf.name_scope('output'):
        if hidden_outputs is None:
            hidden_outputs = inputs
            num_prev_output_units = num_input_units
        else:
            num_prev_output_units = num_hidden_units[num_hidden_layers - 1]

        if given_params is None:
            weights = tf.Variable(
                tf.truncated_normal(
                    [num_prev_output_units, num_output_units],
                    stddev=1.0 / math.sqrt(float(num_prev_output_units))),
                name='weights')
            biases = tf.Variable(
                tf.zeros([num_output_units]),
                name='biases')
            params.extend([weights, biases])
        else:
            weights = given_params[param_num]
            param_num += 1
            biases = given_params[param_num]
            param_num += 1

        outputs = output_activation_function(
            tf.matmul(hidden_outputs, weights) + biases)

    return outputs, params


def training(cost, optimizer_type, learning_rate):
    optimizer = get_optimizer(optimizer_type, learning_rate)
    global_step = tf.Variable(0, name='global_step', trainable=False)
    train_op = optimizer.minimize(cost, global_step=global_step)
    return train_op


def cost(predicted_outputs, observed_outputs, error_adjustments):
    cost = tf.reduce_mean(tf.square(tf.div(
        predicted_outputs - observed_outputs, error_adjustments)))
    return cost
