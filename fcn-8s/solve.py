from __future__ import division
import sys
sys.path.append("/home/lancy/caffe/python")
import caffe
import numpy as np


# make a bilinear interpolation kernel
# credit @longjon
def upsample_filt(size):
    factor = (size + 1) // 2
    if size % 2 == 1:
        center = factor - 1
    else:
        center = factor - 0.5
    og = np.ogrid[:size, :size]
    return (1 - abs(og[0] - center) / factor) * \
           (1 - abs(og[1] - center) / factor)

# set parameters s.t. deconvolutional layers compute bilinear interpolation
# N.B. this is for deconvolution without groups
def interp_surgery(net, layers):
    for l in layers:
        m, k, h, w = net.params[l][0].data.shape
        if m != k:
            print 'input + output channels need to be the same'
            raise
        if h != w:
            print 'filters need to be square'
            raise
        filt = upsample_filt(h)
        net.params[l][0].data[range(m), range(k), :, :] = filt



base_weights = "/data/VGG16/caffemodel"
# base_weights = "../fcn-32s2/good.caffemodel"
# base_weights = "train_iter_400000.caffemodel"

caffe.set_mode_gpu()
caffe.set_device(1)

solver = caffe.SGDSolver("solver.prototxt")

# do net surgery to set the deconvolution weights for bilinear interpolation
interp_layers = [k for k in solver.net.params.keys() if 'up' in k]
interp_surgery(solver.net, interp_layers)

solver.net.copy_from(base_weights)

solver.step(600000)
