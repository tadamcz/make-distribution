from scipy import optimize
from scipy import stats
import math
import numpy as np
import matplotlib.pyplot as plt
import time

# try:
#    google_colab
# except NameError:
# 	################################
# 	### Enter values below ===> ####
# 	###############################
#
# 	# Instructions:
# 	# Choose a distribution family.
# 	# Provide quantiles for the distribution
#
# 	# family can be 'normal', 'lognormal', 'metalog'
# 	family = 'metalog'
#
# 	# Bounds for metalog
# 	# The metalog distribution can be unbounded, or bounded to the left, or the right, or both
# 	# Specify between 0 and 2 bounds, leaving the others as None
# 	metalog_leftbound = None
# 	metalog_rightbound = None
#
# 	# a list of (p,x) tuples, where P(X<x)=p
# 	# (If you provide more than two quantiles for a 2-parameter distribution.
# 	# least squares will be used for fitting. You may provide unlimited
# 	# quantiles for the metalog distribution)
# 	quantiles = [(0,1),(0.05,2),(0.5,7),(0.75,20)]
#
# 	# list of quantiles to print
# 	quantiles_out = [0.01,0.1,0.25,0.5,0.75,0.9,0.99]
#
# 	# Override defaults for domain to plot?
# 	# example: domain_override = [-50,100]
# 	domain_override = None
#
# 	# This many samples
# 	nsamples = 5000
#
# 	################################
# 	### <=== Enter values above ####
# 	################################

def main(dictionary):
	family = dictionary['family']
	quantiles = dictionary['pairs']
	domain_override = None
	quantiles_out = [0.01,0.1,0.25,0.5,0.75,0.9,0.99]	# list of quantiles to print
	nsamples = 5000
	textout = []
	def normal_parameters(x1, p1, x2, p2):
		"Find parameters for a normal random variable X so that P(X < x1) = p1 and P(X < x2) = p2."
		denom = stats.norm.ppf(p2) - stats.norm.ppf(p1)
		sigma = (x2 - x1) / denom
		mu = (x1*stats.norm.ppf(p2) - x2*stats.norm.ppf(p1)) / denom
		return (mu, sigma)

	def quantiles_to_list(quantiles):
		out =[]
		i = 1
		c = 1
		for p,q in quantiles:
			if c == len(quantiles):
				number_to_append = int(100 - i)
			else:
				number_to_append = int(p*100-i)
			out += [q]*number_to_append
			i = p*100
			c += 1
		return out

	def initial_guess_params(quantiles):
		lis = quantiles_to_list(quantiles)
		mean = np.mean(lis)
		stdev = np.std(lis)
		return mean,stdev


	if family =='normal':
		if len(quantiles)==2:
			textout.append('Two quantiles provided, using exact fit \n')
			mu,sigma = normal_parameters(quantiles[0][1],quantiles[0][0],quantiles[1][1],quantiles[1][0])


		if len(quantiles)>2:
			textout.append('More than two quantiles provided, using least squares fit')

			mu_init,sigma_init = initial_guess_params(quantiles)

			fit = optimize.curve_fit(
				lambda x,mu,sigma: stats.norm(mu,sigma).cdf(x),
				xdata=[x[1] for x in quantiles],
				ydata=[x[0] for x in quantiles],
				p0 = [mu_init,sigma_init]
			)

			mu, sigma = fit[0]

		textout.append('Normal distribution')
		textout.append(str(('mu', mu)))
		textout.append(str(('sigma', sigma)))

		def pdf(x):
			return stats.norm.pdf(x,loc=mu,scale=sigma)
		def cdf(x):
			return stats.norm.cdf(x,loc=mu,scale=sigma)
		def ppf(x):
			return stats.norm.ppf(x,loc=mu,scale=sigma)
		def rvs(n):
			return stats.norm.rvs(size=n,loc=mu,scale=sigma)

	if family == 'lognormal':
		if len(quantiles)==2:
			textout.append('Two quantiles provided, using exact fit \n')
			(p1,q1),(p2,q2) = quantiles
			mu,sigma = normal_parameters(math.log(q1),p1,math.log(q2),p2)

		if len(quantiles)>2:
			textout.append('More than two quantiles provided, using least squares fit \n')
			quantiles_logtransformed = [(p,math.log(q)) for p,q in quantiles]
			mu_init,sigma_init = initial_guess_params(quantiles_logtransformed)

			fit = optimize.curve_fit(
				lambda x,mu,sigma: stats.norm(mu,sigma).cdf(x),
				xdata=[q for p,q in quantiles_logtransformed],
				ydata=[p for p,q in quantiles_logtransformed],
				p0 = [mu_init,sigma_init]
			)

			mu, sigma = fit[0]

		textout.append('Lognormal distribution')
		textout.append( str(('mu', mu)))
		textout.append(str(('sigma', sigma)))

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
		def rvs(n):
			return stats.lognorm.rvs(size=n,s=sigma,scale=math.exp(mu))

	if family == 'beta':
		for p,q in quantiles:
			if not 0<=q<=1:
				raise ValueError("Quantiles out of bounds. Beta distribution defined on [0,1]")

		alpha_init, beta_init = 1,1

		fit = optimize.curve_fit(
			lambda x, alpha, beta: stats.beta(alpha, beta).cdf(x),
			xdata=[x[1] for x in quantiles],
			ydata=[x[0] for x in quantiles],
			p0=[alpha_init, beta_init]
		)

		alpha,beta = fit[0]

		textout.append('Beta distribution, using least squares fit \n')
		textout.append(str(('alpa', alpha)))
		textout.append( str(('beta', beta)))

		def pdf(x):
			return stats.beta.pdf(x,alpha,beta)
		def cdf(x):
			return stats.beta.cdf(x,alpha,beta)
		def ppf(x):
			return stats.beta.ppf(x,alpha,beta)
		def rvs(n):
			return stats.beta.rvs(alpha,beta,size=n)

	# create ouput for non-metalog
	if family != 'metalog':
		def guess_domain_to_plot(points=50):
			if domain_override is not None:
				left,right = domain_override
			else:
				left, right = ppf(0.01), ppf(0.99)
			return np.linspace(left, right, points)

		domain_to_plot = guess_domain_to_plot()

		fig, (ax1, ax2) = plt.subplots(2,1)
		ax1.plot(domain_to_plot,cdf(domain_to_plot))
		if quantiles:
			ax1.plot([x[1] for x in quantiles],[x[0] for x in quantiles],'b+')
		ax1.set_title('CDF')
		ax2.plot(domain_to_plot,pdf(domain_to_plot))
		ax2.set_title('PDF')
		graphout = fig

		textout.append("quantiles:\n")
		for x in quantiles_out:
			textout.append(str((x,ppf(x))))

		# taking out the below, since less useful without metalog
		# textout.append("samples:\n")
		# textout.append( str([i for i in rvs(nsamples)]))
	return graphout,textout