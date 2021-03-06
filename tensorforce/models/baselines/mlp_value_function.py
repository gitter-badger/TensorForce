# Copyright 2017 reinforce.io. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""
Multi-layer perceptron baseline value function
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import tensorflow as tf
import numpy as np

from tensorforce.models.baselines.value_function import ValueFunction
from tensorforce.models.neural_networks.layers import dense


class MLPValueFunction(ValueFunction):

    def __init__(self, session=None, update_iterations=100, layer_size=64):
        self.session = session
        self.mlp = None
        self.update_iterations = update_iterations
        self.layer_size = layer_size
        self.labels = tf.placeholder(tf.float32, shape=[None], name="labels")

    def predict(self, path):
        if self.mlp is None:
            return np.zeros(len(path["rewards"]))
        else:
            return self.session.run(self.mlp, {self.input: self.get_features(path)})

    def fit(self, paths):
        feature_matrix = np.concatenate([self.get_features(path) for path in paths])

        if self.mlp is None:
            self.create_net(feature_matrix.shape[1])

        returns = np.concatenate([path["returns"] for path in paths])

        for _ in range(self.update_iterations):
            self.session.run(self.update, {self.input: feature_matrix, self.labels: returns})

    def create_net(self, input_shape):
        with tf.variable_scope("mlp_value_function"):
            self.input = tf.placeholder(tf.float32, shape=[None, input_shape], name="input")

            hidden_1 = dense(self.input, {'num_outputs': input_shape}, 'hidden_1')
            hidden_2 = dense(hidden_1, {'num_outputs': self.layer_size}, 'hidden_2')
            out = dense(hidden_2, {'num_outputs': 1}, 'out')
            self.mlp = tf.reshape(out, (-1,))

            l2 = tf.nn.l2_loss(self.mlp - self.labels)
            self.update = tf.train.AdamOptimizer().minimize(l2)

            self.session.run(tf.global_variables_initializer())
