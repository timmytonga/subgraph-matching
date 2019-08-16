"""
functions for finding data on the desghidorah.
"""

import os
from glob import glob

root_folder = "/s2/scr/reu_data/darpa_maa/data/"

TA1_TEAMS = ["GORDIAN", "IVYSYS", "PNNL","EXAMPLE", "TIM"]

def get_data_dir(data_root,
                 ta1_team=None,
                 version=None,
                 model=None,
                 instance=None):
    """
    Returns the path to the requested data directory on the math server.

    example usage:

        get_data_dir(ta1_team="pnnl", version=1)

    should return the directory containing the PNNL version 1 data.

        get_data_dir(ta1_team="pnnl", version=2, instance=7)

    should return the PNNL V2 7K directory
    """
    ta1_team = ta1_team.upper()
    # assert ta1_team in TA1_TEAMS
    dataset_root = os.path.join(data_root, ta1_team, "V{}".format(version))
    assert os.path.isdir(dataset_root)
    if ta1_team == "PNNL":
        if version == "RW" or version == 1:
            return dataset_root
        elif version == 2:
            assert instance in [7, 50, 100]
            return os.path.join(dataset_root, "{}K".format(instance))
        elif version >= 3:
            if version == 3:
                assert instance in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            elif version == 4:
                assert instance in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            elif version == 5:
                assert model in ["10K", "5M"]
                if model == "10K":
                    assert instance in [x for x in range(12)]
                elif model == "5M":
                    assert instance in [1]
                return os.path.join(dataset_root, model, "B{}".format(instance))
            elif version == 6:
                assert instance in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            else:
                raise Exception("Version {} not supported quite yet." \
                                .format(version))
            return os.path.join(dataset_root, "B{}".format(instance))
    elif ta1_team == "IVYSYS":
        # IVYSYS releases are historically ony instance per version
        return dataset_root
    elif ta1_team == "GORDIAN":
        if version <= 4:
            assert model in ["probabilistic", "agent-based"]
            dataset_root = os.path.join(dataset_root, model)
        if version == 2:
            return dataset_root
        elif version == 3:
            if model == "probabilistic":
                dataset_root = os.path.join(dataset_root, "2018-03-21_Delivery")
            return dataset_root
        elif version == 4:
            if model == "agent-based":
                assert instance in [5, 10, 35]
                return os.path.join(dataset_root, "{}M-edges".format(instance))
            elif model == "probabilistic":
                assert instance in [5000, 10000, 35000]
                return os.path.join(dataset_root, "{}-nodes".format(instance))
        elif version == 5:
            assert instance in [5, 50]
            return os.path.join(dataset_root, "{}K-nodes".format(instance))
        elif version == 6:
            assert instance in [50]
            return os.path.join(dataset_root, os.path.join("{}K-nodes".format(instance), model))
        elif version == 7:
            assert instance in [100]
            return os.path.join(dataset_root, os.path.join("{}K-nodes".format(instance), model))
        else:
            raise Exception("Version {} not supported quite yet." \
                            .format(version))
    elif ta1_team == "EXAMPLE":
        # Examples all have one instance per version
        return dataset_root

    elif ta1_team == "TIM":
        assert instance in range(10)
        return os.path.join(dataset_root, "B{}".format(instance))


class NetFileGetter:
    def __init__(self,
                 ta1_team=None,
                 version=None,
                 instance=None,
                 model=None):
        self.ta1_team = ta1_team.upper()
        self.version = version
        self.instance = instance
        self.model = model

        self.data_root = root_folder
        if self.ta1_team=="PNNL" and self.version != "RW" and self.version >=5 or\
                self.ta1_team=="GORDIAN" and self.version >= 5 or\
                self.ta1_team=="IVYSYS" and self.version >= 8:
            self.data_root = "/s1/scr/reu_data2/darpa_maa/data/"

        if self.ta1_team == "TIM":  # local for now
            self.data_root = "/s2/scr/reu_data/darpa_maa/tim/subgraph-matching/data/"

        self.net_dir = get_data_dir(self.data_root,
                                    ta1_team=self.ta1_team,
                                    version=self.version,
                                    instance=self.instance,
                                    model=self.model)


    def get_cache_dir(self):
        dir_name_parts = [self.ta1_team.lower()]

        if self.version is not None:
            dir_name_parts.append("v{}".format(self.version))

        if self.model is not None:
            dir_name_parts.append(self.model)

        if self.instance is not None:
            dir_name_parts.append("i{}".format(self.instance))

        cache_dir = os.path.join(self.data_root, ".cache")
        dir_str = os.path.join(cache_dir, "_".join(dir_name_parts))

        return dir_str

    def cache_exists(self):
        return bool(os.path.isdir(self.get_cache_dir()))

    def get_file(self,
                 filename):
        fps = glob(os.path.join(self.net_dir, "{}".format(filename)))
        assert len(fps) == 1, "Ambiguous or null filename requested: {}".format(
                              os.path.join(self.net_dir, "{}".format(filename)))
        return fps[0]

    def get_files(self,
                 filename):
        fps = glob(os.path.join(self.net_dir, "{}".format(filename)))
        assert len(fps) >= 1, "Ambiguous request {}. Had no hits".format(
                              os.path.join(self.net_dir, "{}".format(filename)))
        return sorted(fps)
