import numpy as np 
import os
import cPickle, gzip
import theano 
from theano import tensor as T 
from theano import sharedstreams


class PfileIO(object):

	def __init__(self, datapath):
		self.feats = None	
		self.labels = None
		# self.partCounter = 0
		self.datapath = datapath

		# pfile information
		self.header_size = 32768
		self.feat_start_column = 2
		self.feat_dim = 1024
		self.label_start_column = 442
		self.num_labels = 1

		self.total_frame_num = 0
		self.partition_num = 0
        self.frame_per_partition = 0
        self.end_reading = False


	def loadData(self):
		dirpath, filename = os.path.split(self.datapath)

		if dirpath == '' and not os.path.isfile(datapath):
			new_dirpath = os.path.join(
			os.path.split(__file__)[0],
			'rawdata/',
			filename
			)

		if os.path.isfile(new_dirpath) or datapath == 'speechtrain1.pickle.gz':
			datapath = new_dirpath


		self.f = gzip.open(datapath, 'rb')



	def readpfileInfo(self):
		line = self.f.readline()
		if line.startswith('-pfile_header') == False:
			print "Error:Wrong format"
			exit(1)

		self.header_size = int(line.split(' ')[-1])
        while (not line.startswith('-end')):
            if line.startswith('-num_sentences'):
                self.num_sentences = int(line.split(' ')[-1])
            elif line.startswith('-num_frames'):
                self.total_frame_num = int(line.split(' ')[-1])
            elif line.startswith('-first_feature_column'):
                self.feat_start_column = int(line.split(' ')[-1])
            elif line.startswith('-num_features'):
                self.original_feat_dim = int(line.split(' ')[-1])
            elif line.startswith('-first_label_column'):
                self.label_start_column = int(line.split(' ')[-1])
            elif line.startswith('-num_labels'):
                self.num_labels = int(line.split(' ')[-1])
            line = self.f.readline()

        # set a control variable for setting context window width here ...
		self.feat_dim = 11 * self.original_feat_dim
		# self.frame_per_partition = 


	def readPfile(self):

		self.dtype = np.dtype({'names':['d', 'l'],
								'formats':[('>f', self.original_feat_dim), '>i'],
								'offsets': [self.feat_start_column * 4, self.label_start_column * 4]})

		self.f.seek(self.header_size + 4 * (self.label_start_column + self.num_labels) * self.total_frame_num)
		sentence_offset = struct.unpack(">%di" % (self.num_sentences + 1), self.file_read.read(4 * (self.num_sentences + 1)))
		self.feats = []
		self.labels = []

		#  read the file copied directly from pdnn github... 

		for i in xrange(self.num_sentences):
            num_frames = sentence_offset[i+1] - sentence_offset[i]
            if self.f is file:  # Not a compressed file
                sentence_array = np.fromfile(self.f, self.dtype, num_frames)
            else:
                nbytes = 4 * num_frames * (self.label_start_column + self.num_labels)
                d_tmp = self.f.read(nbytes)
                sentence_array = np.fromstring(d_tmp, self.dtype, num_frames)

            feats = np.asarray(sentence_array['d'])
            labels = np.asarray(sentence_array['l'])

            # feat_mat, label_vec = preprocess_feature_and_label(feat_mat, label_vec, self.read_opts)
            
            if len(self.feats) > 0 and read_frames < self.frame_per_partition:
                num_frames = min(len(feats), self.frame_per_partition - read_frames)
                self.feats[-1][read_frames : read_frames + num_frames] = feats[:num_frames]
                self.labels[-1][read_frames : read_frames + num_frames] = labels[:num_frames]
                feat_mat = feat_mat[num_frames:]
                label_vec = label_vec[num_frames:]
                read_frames += num_frames
            if len(feat_mat) > 0:
                read_frames = len(feat_mat)
                self.feats.append(np.zeros((self.frame_per_partition, self.feat_dim), dtype = theano.config.floatX))
                self.labels.append(np.zeros(self.frame_per_partition, dtype = np.int32))
                self.feats[-1][:read_frames] = feat_mat
                self.labels[-1][:read_frames] = label_vec


        # finish reading; close the file
        self.f.close()
        self.feats[-1] = self.feats[-1][:read_frames]
        self.labels[-1] = self.labels[-1][:read_frames]

        self.partition_num = len(self.feats)
        self.partition_index = 0



    def load_next_partition(self, shared_xy):
        feat = self.feats[self.partition_index]
        label = self.labels[self.partition_index]

        shared_x, shared_y = shared_xy

        shared_x.set_value(feat.astype(theano.config.floatX), borrow=True)
        shared_y.set_value(feat.astype(theano.config.floatX), borrow=True)

        self.cur_frame_num = len(feat)
        























