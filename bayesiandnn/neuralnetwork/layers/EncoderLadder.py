import  numpy as np
import theano
import theano.tensor as T 
from collections import OrderedDict
from theano.tensor.shared_randomstreams import RandomStreams 

# layer could be of three types: 1. first layer 2. hidden layer 3.final softmax layer
class EncoderLadder(object):

	def __init__(self, x_labelled, x_unlabelled, n_outputs, gamma=1.0, beta=0.0, rstream=None, activation='tanh', noise_std=0.0, layer_type='hidden'):
		self.layer_type = layer_type
		self.n_outputs = n_outputs
		self.rstream = rstream
		self.layer_values = {}
		self.n_inputs = x_labelled.shape[0]
		self.n_outputs = n_outputs 
		self.num_labels = x_labelled.shape[1]
		self.num_unlabels = x_unlabelled.shape[1]
		self.samples = self.num_labels + self.num_unlabels

		self.W = theano.shared(
            	value=np.asarray(
                	rng.uniform(
                    	low=-6*np.sqrt(6. / (n_inputs + n_outputs)),
                    	high=6*np.sqrt(6. / (n_inputs + n_outputs)),
                    	size=(n_inputs, n_outputs)
                	),
                	dtype=theano.config.floatX),
           	 name='W',
            	borrow=True
        	)

        	self.params = []		
		self.x_combined = self.join(self.x_labelled, self.x_unlabelled)
        	self.layer_values['W'] = self.W
        	self.join = lambda x,y: T.concatenate([x, y], axis=0)
		self.x_l = lambda x:x[:N,:]
		self.x_ul = lambda x:x[N:,:]
		self.split = lambda x: (self.x_l(x), self.x_ul(x))
		self.rstream = RandomStreams(seed=11111)
		self.d = {}
		self.d['labelled'] = {}
		self.d['unlabelled'] = {}

		if self.layer_type == 'input':
			self.h = noise_std * self.gen_gaussian_noise(self.x_combined) + self.x_combined 
			self.z = self.h
		else:
			self.calculate_Params()

			h_l, h_ul = self.split(self.h)
			self.d['labelled']['h'] = h_l
			self.d['unlabelled']['h'] = h_ul	



	def calculateParams(self, x):
		z_pre = T.dot(self.x_combined, self.W) 


		self.z_pre = z_pre
		self.z_enc = z_enc
		# concatenating the input to one vector

		self.z_pre_l = z_pre[:self.num_labels,:]
		self.z_pre_ul = z_pre[self.num_labels:,:]

		# @TODO: introduce momentum to reduce the speed of updating of variables, very important ...

	        #  one more hyper-parameter which controls the amount of noise to be added to the original input.
		self.noise_std = noise_std
		self.gamma = theano.shared(value=np.ones_like(n_outputs)*gamma) 
		self.beta = theano.shared(value=np.zeros_like(n_outputs) + beta)

		self.mu_l, self.sigma_l =  self.calculate_moments(self.z_pre_l)
		self.mu_ul, self.sigma_ul = self.calculate_moments(self.z_pre_ul)
		z_l = self.batch_normalize(self.z_pre_l)
		z_ul = self.batch_normalize(self.z_pre_ul)
		z = self.join(z_l, z_ul)
		self.d['labelled']['mu'] = self.mu_l
		self.d['unlabelled']['mu'] = self.mu_ul
		self.d['labelled']['sigma'] = self.sigma_l
		self.d['unlabelled']['sigma'] = self.sigma_ul
		self.d['labelled']['z_pre'] = z_pre_l
		self.d['unlabelled']['z_pre'] = z_pre_ul
		z = z + self.gen_gaussian_noise(z)*self.noise_std
		self.d['labelled']['z'], self.d['unlabelled']['z'] = self.split(z) 

		self.z = z
		# final layer activation can only be softmax function ... 
		if self.layer_type == 'final':
			activation = 'softmax'
			activation_fn = "T.nnet." + 'Softmax'
			h = T.nnet.Softmax(self.gamma* (self.z + self.beta))
			h = activation_fn(self.z)
		else:
			activation = activation
			activation_fn = "T.nnet." + "relu"
			h = activation_fn(self.z)
		self.h = h

	def _calculate_moments(self, x):
		mu = T.mean(x, axis=1)
    		sigma = T.var(x, axis=1)
    		return mu, sigma


	def get_layer_vals(self):
		return self.h, self.d


	def get_layer_params(self):
		self.params = [self.W, self.gamma, self.beta]
	        return self.params


    	def batch_normalize(self, z, mean=None, var=None):
    		mu = mean
    		sigma = var
    		if not mu or not sigma:
    			mu, sigma = self._calculate_moments(z)
    		mu_mat = mu.dimshuffle(0,'x')
    		sigma_mat = sigma.dimshuffle(0, 'x')
    		z_norm = (z - mu_mat) / (T.sqrt(sigma_mat + 1e-10))
    		return z_norm


# @TODO: move this to general utils folder, ok for the first draft now .....
    	def gen_gaussian_noise(self, x):
    		noise = self.rstream.normal(size=x.shape, avg=0.0, std=1.0)
    		return T.cast(noise, dtype=x.dtype)


    	def update_batch_normalize(self, x):
    		pass

