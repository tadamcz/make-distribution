from scipy import optimize
from scipy import stats
import math
import numpy as np
import matplotlib.pyplot as plt
import time
import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

################################
### Enter values below ===> ####
################################

# Instructions:
# Choose a distribution family.
# Provide either percentiles or parameters for the distribution.

# family can be 'normal', 'lognormal', 'metalog'
family = 'lognormal'


# a list of (p,x) tuples, where P(X<x)=p
'''(If you provide more than two percentiles for a 2-parameter distribution.
 least squares will be used for fitting. You may provide unlimited
 percentiles for the metalog distribution)'''
percentiles = [(0.1,50),(0.5,70),(0.6,75),(0.65,100)]

# parameters for distribution
# (currently only normal and lognormal are supported, so the
# parameters are mu and sigma).
mu,sigma = None,None

# list of percentiles to print
percentiles_out = [0.01,0.1,0.25,0.5,0.75,0.9,0.99]

################################
### <=== Enter values above ####
################################

# todo: bounds for metalog

# argument checking
if [mu,sigma].count(None)<2 and percentiles is not None:
	raise ValueError("You must provide at most one of percentiles and parameters")

if [mu,sigma,percentiles].count(None)==3:
	raise ValueError("You must provide at least one of percentiles and parameters")

if family == 'metalog' and [mu,sigma].count(None)<2:
	raise ValueError("Cannot provide parameters with metalog distribution. Choose another distribution family")

# todo: implement beta distribution: https://stats.stackexchange.com/questions/112614/determining-beta-distribution-parameters-alpha-and-beta-from-two-arbitrary

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
	print("Meta-logistic distribution")
	term = len(percentiles)
	step_len = 0.01

	s = time.time()
	# import R's utility package
	utils = rpackages.importr('utils')

	# select a mirror for R packages
	utils.chooseCRANmirror(ind=1)  # select the first mirror in the list

	# install and import rmetalog
	packnames = ['rmetalog']
	names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
	if len(names_to_install) > 0:
		utils.install_packages(robjects.StrVector(names_to_install))

	rpackages.importr('rmetalog')
	e = time.time()
	print(e-s,'seconds to create R instance and import packages')

	r_metalog_func = robjects.r('''
	function(x,probs,boundedness,term_limit,step_len) {
			  metalog(
				  x = x,
				  probs = probs,
				  boundedness = 'u',
				  term_limit = term_limit,
				  step_len=step_len)
				}
	''')

	r_pmetalog_func = robjects.r('''
	function (metalog_obj,q,term) {
		pmetalog(
			metalog_obj,
			q=q,
			term=term
		)
	}''')

	r_dmetalog_func = robjects.r('''
	function (metalog_obj,q,term) {
		dmetalog(
			metalog_obj,
			q=q,
			term=term
		)
	}''')

	r_qmetalog_func = robjects.r('''
		function (metalog_obj,y,term) {
			qmetalog(
				metalog_obj,
				y=y,
				term=term
			)
		}''')


	r_x = robjects.FloatVector([q for p, q in percentiles])
	r_probs = robjects.FloatVector([p for p, q in percentiles])
	boundedness = 'u'
	r_term_limit = robjects.FloatVector([term])
	r_step_len = robjects.FloatVector([step_len])

	s = time.time()
	r_metalog_obj = r_metalog_func(x=r_x, probs=r_probs, boundedness=boundedness, term_limit=r_term_limit,
								   step_len=r_step_len)
	e = time.time()
	print(e-s,"seconds to fit metalog object")


	domain_to_plot_left,domain_to_plot_right = r_qmetalog_func(metalog_obj=r_metalog_obj, y=robjects.FloatVector([0.01,0.99]), term=r_term_limit)
	domain_to_plot = np.linspace(domain_to_plot_left,domain_to_plot_right,50)

	r_domain = robjects.FloatVector(domain_to_plot)
	r_percentiles_out = robjects.FloatVector(percentiles_out)

	s = time.time()
	cdf_values = r_pmetalog_func(metalog_obj=r_metalog_obj, q=r_domain, term=r_term_limit)
	pdf_values = r_dmetalog_func(metalog_obj=r_metalog_obj, q=r_domain, term=r_term_limit)
	e = time.time()
	print(e-s,"seconds to compute cdf and pdf")

	quantiles_values = r_qmetalog_func(metalog_obj=r_metalog_obj, y=r_percentiles_out, term=r_term_limit)

	# create ouput for metalog
	fig, (ax1, ax2) = plt.subplots(2,1)
	ax1.plot([x[1] for x in percentiles],[x[0] for x in percentiles],'b+')

	ax1.plot(domain_to_plot,cdf_values)
	ax1.set_title('CDF')
	ax2.plot(domain_to_plot,pdf_values)
	ax2.set_title('PDF')
	plt.show()

	print("Percentiles:")
	for i in range(len(percentiles_out)):
		print(percentiles_out[i],quantiles_values[i])

if family =='normal':
	if percentiles:
		if len(percentiles)==2:
			print('Two percentiles provided, using exact fit')
			mu,sigma = normal_parameters(percentiles[0][1],percentiles[0][0],percentiles[1][1],percentiles[1][0])


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

	else:
		pass


	print('Normal distribution')
	print('mu', mu)
	print('sigma', sigma)

	def pdf(x):
		return stats.norm.pdf(x,loc=mu,scale=sigma)
	def cdf(x):
		return stats.norm.cdf(x,loc=mu,scale=sigma)
	def ppf(x):
		return stats.norm.ppf(x,loc=mu,scale=sigma)

if family == 'lognormal':
	if percentiles:
		if len(percentiles)==2:
			print('Two percentiles provided, using exact fit')
			(p1,q1),(p2,q2) = percentiles
			mu,sigma = normal_parameters(math.log(q1),p1,math.log(q2),p2)

		if len(percentiles)>2:
			print('More than two percentiles provided, using least squares fit')
			percentiles_logtransformed = [(p,math.log(q)) for p,q in percentiles]
			mu_init,sigma_init = initial_guess_params(percentiles_logtransformed)

			fit = optimize.curve_fit(
				lambda x,mu,sigma: stats.norm(mu,sigma).cdf(x),
				xdata=[q for p,q in percentiles_logtransformed],
				ydata=[p for p,q in percentiles_logtransformed],
				p0 = [mu_init,sigma_init]
			)

			mu, sigma = fit[0]
	else:
		pass

	print('Lognormal distribution')
	print('mu', mu)
	print('sigma', sigma)

	'''From scipy docs:
	A common parametrization for a lognormal random variable Y is in terms of the mean,
	mu, and standard deviation, sigma, of the unique normally distributed random variable
	X such that exp(X) = Y. This parametrization corresponds to setting s = sigma
	and scale = exp(mu).
	'''
	def pdf(x):
		return stats.lognorm.pdf(x,s=sigma,scale=math.exp(mu))
	def cdf(x):
		return stats.lognorm.cdf(x,s=sigma,scale=math.exp(mu))
	def ppf(x):
		return stats.lognorm.ppf(x,s=sigma,scale=math.exp(mu))

# create ouput for non-metalog
if family != 'metalog':
	def guess_domain_to_plot(points=50):
		left, right = ppf(0.01), ppf(0.99)
		return np.linspace(left, right, points)

	domain_to_plot = guess_domain_to_plot()

	fig, (ax1, ax2) = plt.subplots(2,1)
	ax1.plot(domain_to_plot,cdf(domain_to_plot))
	if percentiles:
		ax1.plot([x[1] for x in percentiles],[x[0] for x in percentiles],'b+')
	ax1.set_title('CDF')
	ax2.plot(domain_to_plot,pdf(domain_to_plot))
	ax2.set_title('PDF')

	print("Percentiles:")
	for x in percentiles_out:
		print(x,ppf(x))

	plt.show()