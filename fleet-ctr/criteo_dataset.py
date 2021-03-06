#   Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
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

import paddle.fluid.incubate.data_generator as dg
import sys
import os

class CriteoDataset(dg.MultiSlotDataGenerator):

    def set_config(self, feature_names):
        self.feature_names = feature_names
        self.feature_dict = {}
        for idx, name in enumerate(self.feature_names):
            self.feature_dict[name] = idx

    def generate_sample(self, line):
        """
        Read the data line by line and process it as a dictionary
        """
        hash_dim_ = int(os.environ['SPARSE_DIM'])
        def reader():
            group = line.strip().split()
            label = int(group[1])
            click = group[0]
            features = []
            for i in range(len(self.feature_names)):
                features.append([])
            for fea_pair in group[2:]:
                feasign, slot = fea_pair.split(":")
                if slot not in self.feature_dict:
                    continue
                features[self.feature_dict[slot]].append(int(feasign) % hash_dim_)
            for i in range(len(features)):
                if features[i] == []:
                    features[i].append(0)
            features.append([label])
            yield zip(self.feature_names + ["label"], features)
        return reader


d = CriteoDataset()
feature_names = []
with open(sys.argv[1]) as fin:
    for line in fin:
        feature_names.append(line.strip())
d.set_config(feature_names)
d.run_from_stdin()
