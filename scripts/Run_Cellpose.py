# Run Cellpose

import numpy as np
from cellpose import models, core, io, plot
from pathlib import Path
from tqdm import trange
import matplotlib.pyplot as plt
from natsort import natsorted
import os 

out_dir = "/storage/scratch01/groups/ce/BLCA_Spatial/CELLPOSE/cellpose_outs"
os.makedirs(out_dir, exist_ok=True)

io.logger_setup() # run this to get printing of progress

#Check if colab notebook instance has GPU access
if core.use_gpu()==False:
  raise ImportError("No GPU access, change your runtime")

model = models.CellposeModel(gpu=True)

img = io.imread("/storage/scratch01/groups/ce/BLCA_Spatial/TMA_3_4/AL-7332_99B-15848-3D_3_97-47941S_4_clean.tif")

first_channel = '0' # @param ['None', 0, 1, 2, 3, 4, 5]
second_channel = '1' # @param ['None', 0, 1, 2, 3, 4, 5]
third_channel = '2' # @param ['None', 0, 1, 2, 3, 4, 5]

selected_channels = []
for i, c in enumerate([first_channel, second_channel, third_channel]):
  if c == 'None':
    continue
  if int(c) > img.shape[-1]:
    assert False, 'invalid channel index, must have index greater or equal to the number of channels'
  if c != 'None':
    selected_channels.append(int(c))

img_selected_channels = np.zeros_like(img)
img_selected_channels[:, :, :len(selected_channels)] = img[:, :, selected_channels]

flow_threshold = 0.4
cellprob_threshold = 0.0
tile_norm_blocksize = 0

masks, flows, styles = model.eval(img_selected_channels, batch_size=32, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold,
                                  normalize={"tile_norm_blocksize": tile_norm_blocksize})

masks_path = out_dir + 'masks_cellpose.tif'
io.imsave(masks_path, masks.astype(np.uint32))
np.save(out_dir + 'masks_cellpose.npy', masks.astype(np.uint32))
print('Mascaras guardadas en', masks_path, flush=True)


try:
    fig = plt.figure(figsize=(12, 5))
    plot.show_segmentation(fig, img_selected_channels, masks, flows[0])
    plt.tight_layout()
    plt.savefig(out_dir + '/segmentacion_cellpose.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('Figura guardada.', flush=True)
except Exception as e:
    print('La figura fallo:', repr(e), flush=True)
 
print('Terminado.', flush=True)