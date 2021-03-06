#!/usr/bin/env python3

#  Copyright 2017 Project Mahjong. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from dqns.dqn_prioritised_memory_interface import *

prioritized_replay_epsilon = 1e-6


class PrioritisedDoubleDQN(DQNPrioritisedMemoryInterface):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractstaticmethod
    def _create_model(input_shape=None, action_count=None):
        raise Exception("Do not call abstract method.")

    def _train_on_memory(self, observation_batch,
                         action_batch,
                         reward_batch,
                         observation_next_batch,
                         done_batch,
                         weights=None,
                         batch_indexes=None):
        q_values = self._model.predict(observation_batch)
        next_q_values = self._model.predict(observation_next_batch)
        next_q_values_target = self._target_model.predict(observation_next_batch)
        td_error = np.array([0.0]*self._replay_memory_batch_size)
        for i in range(self._replay_memory_batch_size):
            if done_batch[i]:
                update_q_value = reward_batch[i]
            else:
                update_q_value = \
                    reward_batch[i] + \
                    self._gamma * next_q_values_target[i][np.argmax(next_q_values[i])]
            td_error[i] = update_q_value - q_values[i][action_batch[i]]
            q_values[i][action_batch[i]] = update_q_value

        # Update prioritised memory priorities.
        new_priorities = np.abs(td_error) + prioritized_replay_epsilon
        self._replay_memory.update_priorities(batch_indexes, new_priorities)

        # Add loss to the plot.
        train_metrics = self._model.train_on_batch(observation_batch, q_values)
        self._losses.append(train_metrics[0] if type(train_metrics) is list else train_metrics)

    @staticmethod
    @abstractstaticmethod
    def _pre_process(input_data):
        raise Exception("Do not call abstract method.")
