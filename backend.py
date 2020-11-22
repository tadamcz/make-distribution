from scipy import optimize
from scipy import stats
import math
import numpy as np
import matplotlib.pyplot as plt
import pymetalogadamczewski as pymetalog
import scipy.stats

class DistributionObject:
	def __init__(self,dictionary):
		def pretty(n):
			return np.format_float_scientific(n, precision=4)

		self.family = dictionary['family']
		self.ps = dictionary['ps']
		self.qs = dictionary['qs']
		self.description = []
		n_samples = 5000

		if dictionary['allow_lp']:
			self.fit_method_constraint = 'any'
		else:
			self.fit_method_constraint = 'OLS'

		if self.family == 'metalog':
			self.description.append('Meta-logistic distribution.')
			term = len(self.ps)

			self.boundedness = dictionary['boundedness']

			# This if-else is necessary because of the way pymetalog handles the bounds arguments. Could be something to improve.
			if self.boundedness: # bounded

				self.lower_bound,self.upper_bound = dictionary['lower_bound'],dictionary['upper_bound']
				if self.lower_bound is not None and self.upper_bound is not None:
					pymetalog_boundedness = 'b'
					pymetalog_bounds = [self.lower_bound,self.upper_bound]
				elif self.lower_bound is not None:
					pymetalog_boundedness = 'sl'
					pymetalog_bounds = [self.lower_bound]
				elif self.upper_bound is not None:
					pymetalog_boundedness = 'su'
					pymetalog_bounds = [self.upper_bound]

				self.pymetalog_object = pymetalog.metalog(
					self.qs,
					probs=self.ps,
					term_lower_bound=term,
					term_limit=term,
					fit_method=self.fit_method_constraint,
					boundedness=pymetalog_boundedness,
					bounds=pymetalog_bounds
				)
			else: # unbounded
				self.pymetalog_object = pymetalog.metalog(
					self.qs,
					probs=self.ps,
					term_lower_bound=term,
					term_limit=term,
					fit_method=self.fit_method_constraint
				)

			if self.pymetalog_object.output_dict['Validation'].valid[0] == 'no': #  Good heavens!
				self.description.append('There is no valid metalog for these parameters. Try changing the '
										'parameters or allowing linear program.')
				return
			actual_fit_method = self.pymetalog_object.output_dict['Validation'].method.values[0]
			if actual_fit_method == 'LP':
				actual_fit_method == 'Linear program'
			self.description.append('Fit method: '+actual_fit_method)
			self.generatePlotDataMetalog()
			self.createPlot()
			self.samples = np.array2string(pymetalog.rmetalog(self.pymetalog_object,n=n_samples,term=term).flatten(),
										   separator=', ',
										   threshold=n_samples+1,
										   max_line_width=float('inf'))

		else: #  if not metalog, we deal with a SciPy distribution object
			self.samples = None

			if self.family == 'normal':
				self.description.append('Normal distribution')
				if len(self.ps) == 2:
					self.description.append('Two quantiles provided, using exact fit.')
					mu, sigma = self.normal_parameters(self.qs[0], self.ps[0], self.qs[1], self.ps[1])

					self.description.append('mu: ' + pretty(mu))
					self.description.append('sigma: ' + pretty(sigma))


				if len(self.ps) > 2:
					self.description.append('More than two quantiles provided, using least squares fit.')

					mu_init, sigma_init = self.initial_guess_params()

					fit = optimize.curve_fit(
						lambda x, mu, sigma: stats.norm(mu, sigma).cdf(x),
						xdata=self.qs,
						ydata=self.ps,
						p0=[mu_init, sigma_init]
					)

					(mu, sigma), covariances = fit
					mu_sd , sigma_sd = np.sqrt(np.diag(covariances))

					self.description.append('mu: ' + pretty(mu) + ' (Estimated standard deviation:'+ pretty(mu_sd)+')')
					self.description.append('sigma: ' + pretty(sigma) + ' (Estimated standard deviation:'+ pretty(sigma_sd)+')')

				self.scipy_distribution = scipy.stats.norm(loc=mu,scale=sigma)

			if self.family == 'lognormal':
				self.description.append('Log-normal distribution')
				qs_log_transformed = [math.log(x) for x in self.qs]
				if len(self.ps) == 2:
					self.description.append('Two quantiles provided, using exact fit.')
					mu, sigma = self.normal_parameters(qs_log_transformed[0], self.ps[0], qs_log_transformed[1], self.ps[1])

					self.description.append('mu: ' + pretty(mu))
					self.description.append('sigma: ' + pretty(sigma))

				if len(self.ps) > 2:
					self.description.append('More than two quantiles provided, using least squares fit.')
					mu_init, sigma_init = self.initial_guess_params(self.ps,qs_log_transformed)

					fit = optimize.curve_fit(
						lambda x, mu, sigma: stats.lognorm(s=sigma, scale = math.exp(mu)).cdf(x),
						xdata=self.qs,
						ydata=self.ps,
						p0=[mu_init, sigma_init]
					)

					(mu, sigma), covariances = fit
					mu_sd , sigma_sd = np.sqrt(np.diag(covariances))
					self.description.append('mu: ' + pretty(mu) + ' (Estimated standard deviation:' + pretty(mu_sd) + ')')
					self.description.append('sigma: ' + pretty(sigma) + ' (Estimated standard deviation:' + pretty(sigma_sd) + ')')



				self.scipy_distribution = scipy.stats.lognorm(s=sigma,scale=math.exp(mu))

			if self.family == 'beta':
				for q in self.qs:
					if not 0 <= q <= 1:
						self.description.append("Quantiles out of bounds. Beta distribution defined on [0,1]")
						return

				alpha_init, beta_init = 1, 1

				fit = optimize.curve_fit(
					lambda x, alpha, beta: stats.beta(alpha, beta).cdf(x),
					xdata=self.qs,
					ydata=self.ps,
					p0=[alpha_init, beta_init]
				)

				(alpha, beta), covariances = fit
				alpha_sd, beta_sd = np.sqrt(np.diag(covariances))

				self.description.append('Beta distribution, using least squares fit.')
				self.description.append('alpha: ' + pretty(alpha) + ' (Estimated standard deviation:' + pretty(alpha_sd) + ')')
				self.description.append('beta: ' + pretty(beta) + ' (Estimated standard deviation:' + pretty(beta_sd) + ')')

				self.scipy_distribution = scipy.stats.beta(alpha,beta)

			self.generatePlotDataSciPy()
			self.createPlot()

	def generatePlotDataSciPy(self):
		number_points = 100
		y_bound = 0.001
		left = self.scipy_distribution.ppf(y_bound)
		right = self.scipy_distribution.ppf(1-y_bound)

		if min(self.qs)<left:
			left = min(self.qs)
		if max(self.qs)>right:
			right = max(self.qs)

		self.x_axis = np.linspace(left,right,number_points)

		self.y_axis_cdf = self.scipy_distribution.cdf(self.x_axis)
		self.y_axis_pdf = self.scipy_distribution.pdf(self.x_axis)


	def generatePlotDataMetalog(self):
		term = str(len(self.ps))
		big_M_name = "M" + str(term)
		small_m_name = "m" + str(term)
		self.x_axis = self.pymetalog_object.output_dict['M'][big_M_name]
		self.y_axis_cdf = self.pymetalog_object.output_dict['M']['y']
		self.y_axis_pdf = self.pymetalog_object.output_dict['M'][small_m_name]

	def createPlot(self):
		fig, (cdf_subplot, pdf_subplot) = plt.subplots(2, 1)

		cdf_subplot.set_title('CDF')
		cdf_subplot.plot(self.x_axis,self.y_axis_cdf)
		cdf_subplot.plot(self.qs, self.ps, 'b+')

		pdf_subplot.set_title('PDF')
		pdf_subplot.plot(self.x_axis, self.y_axis_pdf)
		self.plot = fig

	def normal_parameters(self, x1, p1, x2, p2):
		"Find parameters for a normal random variable X so that P(X < x1) = p1 and P(X < x2) = p2."
		denom = stats.norm.ppf(p2) - stats.norm.ppf(p1)
		sigma = (x2 - x1) / denom
		mu = (x1*stats.norm.ppf(p2) - x2*stats.norm.ppf(p1)) / denom
		return (mu, sigma)

	def quantiles_to_list(self,ps=None,qs=None):
		if ps is None:
			ps = self.ps
		if qs is None:
			qs = self.qs
		out =[]
		i = 1
		c = 1
		for p,q in zip(ps,qs):
			if c == len(ps):
				number_to_append = int(100 - i)
			else:
				number_to_append = int(p*100-i)
			out += [q]*number_to_append
			i = p*100
			c += 1
		return out

	def initial_guess_params(self,ps=None,qs=None):
		if ps is None:
			ps = self.ps
		if qs is None:
			qs = self.qs
		lis = self.quantiles_to_list(ps,qs)
		mean = np.mean(lis)
		stdev = np.std(lis)
		return mean,stdev