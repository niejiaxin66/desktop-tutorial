# -*- coding: utf-8 -*-
"""milano_crop.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1b6Xt453_XrJZtwKTAvWMzAzKkSn7AoEs
"""


#import h5py
#import pickle
import numpy as np
from pandas import to_datetime
#from stgcn_traffic_prediction.models.MinMaxNorm import MinMaxNorm01
#from stgcn_traffic_prediction.dataloader.STMatrix import STMatrix
from PeMS04.models.MinMaxNorm import MinMaxNorm01
from PeMS04.dataloader.STMatrix import STMatrix
#####‼execfile('/content/drive/MyDrive/transformer/PeMS04/models/MinMaxNorm.ipynb')
#####‼execfile('/content/drive/MyDrive/transformer/PeMS04/dataloader/STMatrix.ipynb')

 
def _loader(f):
    #data = np.load('/content/ASTGCN/data/PEMS04/pems04.npz') 
    data=np.load(f)     
    return data
    

def load_data(path, closeness_size, period_size, trend_size, len_test):
    f = path
    data0 = _loader(f)
    index = data0['index']

    # wf = h5py.File('data.h5', 'w')
    # wf.create_dataset('data', data=data)
    # wf.create_dataset('idx', data=f['idx'])
    # wf.close()
    data=data0['data'].transpose([1,0,2])[:,:,0][:,:,np.newaxis]
    data=data.transpose([1,0,2])
    
    data_all = [data]
    index_all = [index]

    mmn = MinMaxNorm01()
    data_train = data[:-len_test]
    mmn.fit(data_train)

    data_all_mmn = []
    for data in data_all:
        data_all_mmn.append(mmn.transform(data))

    xc, xp, xt = [], [], []
    y = []
    timestamps_y = []

    for data, index in zip(data_all_mmn, index_all):
        #print(data.shape,index.shape) #(1488,2,400) (1488,)
        st = STMatrix(data, index, 24)
        _xc, _xp, _xt, _y, _timestamps_y = st.create_dataset(
            len_closeness=closeness_size, len_period=period_size, len_trend=trend_size,PeriodInterval=1)

        xc.append(_xc)
        xp.append(_xp)
        xt.append(_xt)
        y.append(_y)
        timestamps_y += _timestamps_y

    xc = np.vstack(xc)
    xp = np.vstack(xp)
    xt = np.vstack(xt)
    y = np.vstack(y)

    xc_train, xp_train, xt_train, y_train = xc[:-len_test], xp[:-len_test], xt[:-len_test], y[:-len_test]
    xc_test, xp_test, xt_test, y_test = xc[-len_test:], xp[-len_test:], xt[:-len_test], y[-len_test:]
    timestamps_train, timestamps_test = timestamps_y[:-len_test], timestamps_y[-len_test:]

    x_train = []
    x_test = []

    for l, x_ in zip([closeness_size, period_size, trend_size], [xc_train, xp_train, xt_train]):
        if l > 0:
            x_train.append(x_)

    for l, x_ in zip([closeness_size, period_size, trend_size], [xc_test, xp_test, xt_test]):
        if l > 0:
            x_test.append(x_)
    return x_train, y_train, x_test, y_test, mmn
