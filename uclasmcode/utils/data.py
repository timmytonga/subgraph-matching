from .data_loaders import pnnl_v2
from .data_loaders import pnnl_v3
from .data_loaders import pnnl_v4
from .data_loaders import pnnl_v5
from .data_loaders import pnnl_v6
from .data_loaders import pnnl_rw
from .data_loaders import pnnl_rw_noisy
from .data_loaders import gordian_v4_agent_based
from .data_loaders import gordian_v4_probabilistic
from .data_loaders import gordian_v5
from .data_loaders import gordian_v6
from .data_loaders import gordian_v7
from .data_loaders import ivysys_v4
from .data_loaders import ivysys_v6
from .data_loaders import ivysys_v7
from .data_loaders import ivysys_v8
from .data_loaders import ivysys_v9
from .data_loaders import transportation
from .data_loaders import foodweb
from .data_loaders import bench_mark

all = []
names = []
for i in [7, 50, 100]:
    all.append(lambda i=i: pnnl_v2(i))
    names.append("pnnl_v2_{}k".format(i))
for i in range(12):
    all.append(lambda i=i: pnnl_v3(i))
    names.append("pnnl_v3_b{}".format(i))
for i in range(10):
    all.append(lambda i=i: pnnl_v4(i))
    names.append("pnnl_v4_b{}".format(i))
for i in range(12):
    all.append(lambda i=i: pnnl_v6(i))
    names.append("pnnl_v6_b{}".format(i))
for i in [5, 10, 35]:
    all.append(lambda i=i: gordian_v4_agent_based(i))
    names.append("gordian_v4_agent_based_{}M".format(i))
for i in [5000, 10000, 35000]:
    all.append(lambda i=i: gordian_v4_probabilistic(i))
    names.append("gordian_v4_probabilistic_{}K".format(i))
for i in [5, 50]:
    all.append(lambda i=i: gordian_v5(i))
    names.append("gordian_v5_{}K".format(i))
all.append(gordian_v6)
names.append("gordian_v6")
all.append(gordian_v7)
names.append("gordian_v7")
all.append(ivysys_v4)
names.append("ivysys_v4")
all.append(ivysys_v6)
names.append("ivysys_v6")
all.append(ivysys_v7)
names.append("ivysys_v7")
all.append(ivysys_v8)
names.append("ivysys_v8")
all.append(ivysys_v9)
names.append("ivysys_v9")
all.append(transportation)
names.append("transportation")
