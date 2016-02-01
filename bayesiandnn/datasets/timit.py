

import numpy as np 
import cPickle, gzip
import os
import theano
import math
# import random
from collections import Counter
from theano import tensor as T
from os import sys, path

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from dataio.pfileio import PfileIO
# from .. import dataio.PickleIO as PickleIO
# 

sys.path.append('~/masters-thesis/bayesiandnn/bayesiandnn/datasets/rawdata')


def _load_raw_data(datapath):
	dirpath, filename = os.path.split(datapath)

	if dirpath == '' and not os.path.isfile(datapath):
		new_dirpath = os.path.join(
			os.path.split(__file__)[0],
			'datasets/rawdata/',
			filename
			)

		if os.path.isfile(new_dirpath) or datapath == '.pickle.gz':
			datapath = new_dirpath

	f = gzip.open(datapath, 'rb')



def readTIMIT(format='pfile'):
	file_reader = PfileIO('tr95.pfile.gz')
	file_reader.readpfileInfo()
	file_reader.readPfile()
	x, y = file_reader.generate_features()
	print x.shape
	# exit(1)
	return x, y


# to seperate the data into training, test and validation sets.
# divide into a ratio of 70,15,15
# use it only for numpy

def make_sets(x, y):
	print x
	indices = x.shape[0]

	seed = 1111
	np.random.seed(seed)
	np.random.shuffle(x)
	np.random.seed(seed)
	np.random.shuffle(y)

	n_train_idx = abs(0.70 * indices)
	n_valid_idx = abs(0.15 * indices)
	n_test_idx = abs(0.15 * indices)

	train_set_x, train_set_y = x[:n_train_idx, :], y[:n_train_idx]
	valid_set_x, valid_set_y = x[n_train_idx:n_train_idx + n_valid_idx, :], y[n_train_idx:n_train_idx + n_valid_idx]
	test_set_x, test_set_y = x[n_train_idx + n_valid_idx:, :], y[n_train_idx + n_valid_idx:]
	return [(train_set_x, train_set_y), (valid_set_x, valid_set_y), (test_set_x, test_set_y)]



def make_shared_sets(x, y):
	[train_set, valid_set, test_set] = make_sets(x, y)

	def shared_dataset(data_xy, borrow = True):
		data_x, data_y = data_xy
		shared_x = theano.shared(np.asarray(data_x, dtype= np.float32), borrow=borrow)
		shared_y = theano.shared(np.asarray(data_y, dtype= np.float32), borrow=borrow)

		return shared_x, T.cast(shared_y, 'int32')

	train_set_x, train_set_y = shared_dataset(train_set)
	valid_set_x, valid_set_y = shared_dataset(valid_set)
	test_set_x, test_set_y = shared_dataset(test_set)
	print train_set_x.get_value().shape[0]

	return [(train_set_x, train_set_y), (valid_set_x, valid_set_y), (test_set_x, test_set_y)]


