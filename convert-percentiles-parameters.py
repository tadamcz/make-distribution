from scipy import optimize
from scipy import stats
import math
import pymetalog as pm
from metalog import metalog
import numpy as np
import matplotlib.pyplot as plt
import time
'''
Get distribution from percentiles

First, choose a distribution family

2-parameter distributions
	normal
	log-normal
	beta

meta-logistic distribution.

If you provide more than two percentiles for a 2-parameter distribution.
least squares will be used for fitting.
'''


################################
### Enter values below ===> ####
################################

# family can be 'normal', 'lognormal', 'beta', 'metalog'
family = 'metalog'

# a list of (p,x) tuples, where P(X<x)=p
percentiles = [(0.1,0),
			   (0.2,50),
			   (0.3,51),
			   (0.4,53),
			   (0.5,70)]


# list of percentiles to print
percentiles_out = [0.01,0.1,0.25,0.5,0.75,0.9,0.99]

################################
### <=== Enter values above ####
################################



percentiles_x_p = [(b,a) for (a,b) in percentiles]


def guess_domain_to_plot(percentiles):
	ps = [q for p,q in percentiles]
	minp = min(ps)
	maxp = max(ps)
	width = maxp-minp
	buffer = 0.2*width
	return np.linspace(minp-buffer,maxp+buffer,50)

domain_to_plot = guess_domain_to_plot(percentiles)


def normal_parameters(x1, p1, x2, p2):
	"Find parameters for a normal random variable X so that P(X < x1) = p1 and P(X < x2) = p2."
	denom = stats.norm.ppf(p2) - stats.norm.ppf(p1)
	sigma = (x2 - x1) / denom
	mu = (x1*stats.norm.ppf(p2) - x2*stats.norm.ppf(p1)) / denom
	return (mu, sigma)

def percentiles_to_list(percentiles):
	out =[]
	i = 1
	c = 1
	for p,q in percentiles:
		if c == len(percentiles):
			number_to_append = int(100 - i)
		else:
			number_to_append = int(p*100-i)
		out += [q]*number_to_append
		i = p*100
		c += 1
	return out

def initial_guess_params(percentiles):
	lis = percentiles_to_list(percentiles)
	mean = np.mean(lis)
	stdev = np.std(lis)
	return mean,stdev

if family == 'metalog':
	term = len(percentiles)

	# metalog_obj = pm.metalog(
	# 	x = [tuple[1] for tuple in percentiles],
	# 	probs =[tuple[0] for tuple in percentiles],
	# 	boundedness = 'u',
	# 	term_limit = term,
	# 	step_len=0.001)

	term = 3 #debugging
	metalog_obj = metalog.fit(
		x = [tuple[1] for tuple in percentiles],
		probs =[tuple[0] for tuple in percentiles],
		boundedness = 'u',
		term_limit = term,
		step_len=0.001)


	print("Percentiles:")

	# Todo: understand why passing term=term does not work, while term=term-1 works
	quantiles = metalog.q(metalog_obj,percentiles_out,term=term)
	for i in range(len(percentiles_out)):
		print(percentiles_out[i],quantiles[i])


	# todo: understand why passing a long domain causes dmetalog and qmetalog to
	# return lists that are too short

	domain_for_debugging = domain_to_plot


	# pdf_values = pm.dmetalog(metalog_obj,domain_for_debugging,term=term)
	# pdf_values = metalog.d(metalog_obj, domain_for_debugging, term=term)
	import rmetalog

	pdf_values = rmetalog.pdf_values

	if len(pdf_values)!=len(domain_for_debugging):
		raise RuntimeError("dmetalog gave",len(pdf_values),"results, instead of",len(domain_for_debugging))

	# cdf_values = pm.pmetalog(metalog_obj,domain_for_debugging,term=term)
	# cdf_values = metalog.p(metalog_obj,domain_for_debugging,term=term)
	cdf_values = rmetalog.cdf_values


	if len(cdf_values)!=len(domain_for_debugging):
		raise RuntimeError("dmetalog gave",len(cdf_values),"results, instead of",len(domain_for_debugging))

	fig, (ax1, ax2) = plt.subplots(2,1)
	ax1.plot([x[1] for x in percentiles],[x[0] for x in percentiles],'b+')

	ax1.plot(domain_for_debugging,cdf_values)
	ax1.set_title('CDF')
	ax2.plot(domain_for_debugging,pdf_values)
	ax2.set_title('PDF')
	plt.show()

if family =='normal':
	if len(percentiles)==2:
		print('Two percentiles provided, using exact fit')
		mu,sigma = normal_parameters(percentiles[0][1],percentiles[0][0],percentiles[1][1],percentiles[1][0])
		print('Normal distribution')
		print('mu',mu)
		print('sigma',sigma)

	if len(percentiles)>2:
		print('More than two percentiles provided, using least squares fit')

		mu_init,sigma_init = initial_guess_params(percentiles)

		fit = optimize.curve_fit(
			lambda x,mu,sigma: stats.norm(mu,sigma).cdf(x),
			xdata=[x[1] for x in percentiles],
			ydata=[x[0] for x in percentiles],
			p0 = [mu_init,sigma_init]
		)

		mu, sigma = fit[0]

	def pdf(x):
		return stats.norm.pdf(x,loc=mu,scale=sigma)
	def cdf(x):
		return stats.norm.cdf(x,loc=mu,scale=sigma)
	def ppf(x):
		return stats.norm.ppf(x,loc=mu,scale=sigma)


## create ouput
if family != 'metalog':
	fig, (ax1, ax2) = plt.subplots(2,1)
	ax1.plot(domain_to_plot,cdf(domain_to_plot))
	ax1.plot([x[1] for x in percentiles],[x[0] for x in percentiles],'b+')
	ax1.set_title('CDF')
	ax2.plot(domain_to_plot,pdf(domain_to_plot))
	ax2.set_title('PDF')


	print("Percentiles:")
	for x in percentiles_out:
		print(x,ppf(x))

	plt.show()


'''
Get percentiles from distribution

Choose a distribution family and provide its parameters
(I can reuse code from bayes-continuous for this)
'''
