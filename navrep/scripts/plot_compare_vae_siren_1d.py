from __future__ import print_function
import numpy as np
import os
from sensor_msgs.msg import LaserScan

from navrep.tools.data_extraction import archive_to_lidar_dataset
from navrep.models.vae1d import Conv1DVAE, reset_graph

DEBUG_PLOTTING = True

# Parameters for training
batch_size = 100
N_SCANS_PER_BATCH = 1
NUM_EPOCH = 100
DATA_DIR = "record"
HOME = os.path.expanduser("~")
MAX_LIDAR_DIST = 25.0

vae_model_path = os.path.expanduser("~/navrep/models/V/vae1d.json")

# create network
reset_graph()
vae = Conv1DVAE(batch_size=batch_size, is_training=False)

# load
vae.load_json(vae_model_path)

# create training dataset
dataset = archive_to_lidar_dataset("~/navrep/datasets/V/ian", limit=180)
if len(dataset) == 0:
    raise ValueError("no scans found, exiting")
print(len(dataset), "scans in dataset.")
dataset = dataset[100000:]

# split into batches:
total_length = len(dataset)
num_batches = len(dataset)


dummy_msg = LaserScan()
dummy_msg.range_max = 100.0
dummy_msg.ranges = range(1080)

batch = dataset[:N_SCANS_PER_BATCH]
scans = batch

obs = np.clip(scans.astype(np.float) / MAX_LIDAR_DIST, 0.0, MAX_LIDAR_DIST)
obs = obs.reshape(N_SCANS_PER_BATCH, 1080, 1)

obs_pred = vae.encode_decode(obs)

from navrep.models.siren1d import SIREN1D, reset_graph

DEBUG_PLOTTING = True

# Parameters for training
batch_size = 1080
N_SCANS_PER_BATCH = 1
NUM_EPOCH = 100
DATA_DIR = "record"
HOME = os.path.expanduser("~")
MAX_LIDAR_DIST = 25.0

siren_model_path = os.path.expanduser("~/navrep/models/V/siren1d.json")

# create network
reset_graph()
siren = SIREN1D(batch_size=batch_size, is_training=False)

# load
siren.load_json(siren_model_path)

# split into batches:
total_length = len(dataset)
num_batches = len(dataset)

dummy_msg = LaserScan()
dummy_msg.range_max = 100.0
dummy_msg.ranges = range(1080)

batch = dataset[:N_SCANS_PER_BATCH]
scans = batch

obs = np.clip(scans.astype(np.float) / MAX_LIDAR_DIST, 0.0, MAX_LIDAR_DIST)
obs = obs.reshape(N_SCANS_PER_BATCH, 1080, 1)

obs_pred2 = siren.encode_decode(obs)

import matplotlib.pyplot as plt

plt.ion()
plt.figure("rings")
plt.cla()
plt.plot(obs[0,:,0])
plt.plot(obs_pred[0,:,0])
plt.plot(obs_pred2[0,:,0])
plt.legend(["true", "convolutional", "SIREN"])
# update
plt.pause(0.01)
