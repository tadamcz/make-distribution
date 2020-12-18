import json
from scipy import optimize
from scipy import stats
import math
import numpy as np
import matplotlib.pyplot as plt
import pymetalogtadamcz.pymetalog as pymetalog
import scipy.stats

class DistributionObject:
	def __init__(self,dictionary):
		self.samples = None
		self.description = []

		self.dictionary = dictionary
		self.family = dictionary['family']
		self.ps = dictionary['ps']
		self.qs = dictionary['qs']

		self.plot_custom_domain = False
		if dictionary['plot_custom_domain_bool']:
			self.plot_custom_domain = (dictionary['plot_custom_domain_left'],dictionary['plot_custom_domain_right'])


		if self.family == 'metalog':
			self.initMetalog()

		else:
			self.initSciPy()

	def initSciPy(self):

		if self.family == 'normal':
			self.description.append('Normal distribution')
			if len(self.ps) == 2:
				self.description.append('Two quantiles provided, using exact fit.')
				mu, sigma = self.normal_parameters(self.qs[0], self.ps[0], self.qs[1], self.ps[1])

				self.description.append('mu: ' + self.pretty(mu))
				self.description.append('sigma: ' + self.pretty(sigma))

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
				mu_sd, sigma_sd = np.sqrt(np.diag(covariances))

				self.description.append('mu: ' + self.pretty(mu) + ' (Estimated standard deviation:' + self.pretty(mu_sd) + ')')
				self.description.append('sigma: ' + self.pretty(sigma) + ' (Estimated standard deviation:' + self.pretty(sigma_sd) + ')')

			self.scipy_distribution = scipy.stats.norm(loc=mu, scale=sigma)

		if self.family == 'lognormal':
			self.description.append('Log-normal distribution')
			qs_log_transformed = [math.log(x) for x in self.qs]
			if len(self.ps) == 2:
				self.description.append('Two quantiles provided, using exact fit.')
				mu, sigma = self.normal_parameters(qs_log_transformed[0], self.ps[0], qs_log_transformed[1], self.ps[1])

				self.description.append('mu: ' + self.pretty(mu))
				self.description.append('sigma: ' + self.pretty(sigma))

			if len(self.ps) > 2:
				self.description.append('More than two quantiles provided, using least squares fit.')
				mu_init, sigma_init = self.initial_guess_params(self.ps, qs_log_transformed)

				fit = optimize.curve_fit(
					lambda x, mu, sigma: stats.lognorm(s=sigma, scale=math.exp(mu)).cdf(x),
					xdata=self.qs,
					ydata=self.ps,
					p0=[mu_init, sigma_init]
				)

				(mu, sigma), covariances = fit
				mu_sd, sigma_sd = np.sqrt(np.diag(covariances))
				self.description.append('mu: ' + self.pretty(mu) + ' (Estimated standard deviation:' + self.pretty(mu_sd) + ')')
				self.description.append('sigma: ' + self.pretty(sigma) + ' (Estimated standard deviation:' + self.pretty(sigma_sd) + ')')

			self.scipy_distribution = scipy.stats.lognorm(s=sigma, scale=math.exp(mu))

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
			self.description.append('alpha: ' + self.pretty(alpha) + ' (Estimated standard deviation:' + self.pretty(alpha_sd) + ')')
			self.description.append('beta: ' + self.pretty(beta) + ' (Estimated standard deviation:' + self.pretty(beta_sd) + ')')

			self.scipy_distribution = scipy.stats.beta(alpha, beta)

		self.generatePlotDataSciPy()
		self.createPlot()

	def initMetalog(self):
		n_samples = 5000
		if self.dictionary['allow_lp']:
			self.fit_method_constraint = 'any'
		else:
			self.fit_method_constraint = 'OLS'
		self.description.append('Meta-logistic distribution.')
		term = len(self.ps)

		self.metalog_boundedness = self.dictionary['metalog_boundedness']

		# This if-else is necessary because of the way pymetalog handles the bounds arguments. Could be something to improve.
		if self.metalog_boundedness:  # bounded

			self.metalog_lower_bound, self.metalog_upper_bound = self.dictionary['metalog_lower_bound'], self.dictionary['metalog_upper_bound']
			if self.metalog_lower_bound is not None and self.metalog_upper_bound is not None:
				pymetalog_boundedness = 'b'
				pymetalog_bounds = [self.metalog_lower_bound, self.metalog_upper_bound]
			elif self.metalog_lower_bound is not None:
				pymetalog_boundedness = 'sl'
				pymetalog_bounds = [self.metalog_lower_bound]
			elif self.metalog_upper_bound is not None:
				pymetalog_boundedness = 'su'
				pymetalog_bounds = [self.metalog_upper_bound]

			self.pymetalog_object = pymetalog.metalog(
				self.qs,
				probs=self.ps,
				term_lower_bound=term,
				term_limit=term,
				fit_method=self.fit_method_constraint,
				boundedness=pymetalog_boundedness,
				bounds=pymetalog_bounds
			)
		else:  # unbounded
			self.pymetalog_object = pymetalog.metalog(
				self.qs,
				probs=self.ps,
				term_lower_bound=term,
				term_limit=term,
				fit_method=self.fit_method_constraint
			)

		if self.pymetalog_object.output_dict['Validation'].valid[0] == 'no':  # Good heavens!
			self.description.append('There is no valid metalog for these parameters. Try changing the '
									'parameters or allowing linear program.')
			return
		actual_fit_method = self.pymetalog_object.output_dict['Validation'].method.values[0]
		if actual_fit_method == 'LP':
			actual_fit_method == 'Linear program'
		self.description.append('Fit method: ' + actual_fit_method)
		self.generatePlotDataMetalog()
		self.createPlot()
		self.samples = np.array2string(pymetalog.rmetalog(self.pymetalog_object, n=n_samples, term=term).flatten(),
									   separator=', ',
									   threshold=n_samples + 1,
									   max_line_width=float('inf'))


	def generatePlotDataSciPy(self):
		number_points = 100
		if self.plot_custom_domain:
			left, right = self.plot_custom_domain

		else:
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
		term = len(self.ps)
		big_M_name = "M" + str(term)
		small_m_name = "m" + str(term)
		self.x_axis = self.pymetalog_object.output_dict['M'][big_M_name]
		self.y_axis_cdf = self.pymetalog_object.output_dict['M']['y']
		self.y_axis_pdf = self.pymetalog_object.output_dict['M'][small_m_name]

		# This is a hacky approach. It would be nicer to allow setting a custom domain for
		# the output_dict of the pymetalog call. But since calling qmetalog() is computationally cheap,
		# it's an OK hack for now.
		if self.plot_custom_domain:
			left, right = self.plot_custom_domain
			y_cdf_bottom, y_cdf_top = pymetalog.pmetalog(self.pymetalog_object,q=[left,right],term=term)
			if isinstance(y_cdf_top,StopIteration) or isinstance(y_cdf_bottom,StopIteration):
				return
			y = np.linspace(y_cdf_bottom,y_cdf_top,100)
			self.y_axis_cdf = y
			self.x_axis = pymetalog.qmetalog(self.pymetalog_object, y=y,term=term)

	def createPlot(self):

		cdf_jsonlike = [{'x': self.x_axis[i], 'y': self.y_axis_cdf[i]} for i in range(len(self.x_axis))]
		pdf_jsonlike = [{'x': self.x_axis[i], 'y': self.y_axis_pdf[i]} for i in range(len(self.x_axis))]

		quantiles_jsonlike = [{'x': self.qs[i], 'y': self.ps[i]} for i in range(len(self.qs))]

		cdf_metadata_jsonlike = dict(xmin=min(self.x_axis), ymin=min(self.y_axis_cdf), xmax=max(self.x_axis), ymax=max(self.y_axis_cdf))
		pdf_metadata_jsonlike = dict(xmin=min(self.x_axis), ymin=min(self.y_axis_pdf), xmax=max(self.x_axis), ymax=max(self.y_axis_pdf))

		js = '''
		<script>
		const cdf_data =''' + json.dumps(cdf_jsonlike) + '''
		const cdf_metadata =''' + json.dumps(cdf_metadata_jsonlike) + '''
		const pdf_data =''' + json.dumps(pdf_jsonlike) + '''
		const pdf_metadata =''' + json.dumps(pdf_metadata_jsonlike) + '''
		const quantiles =''' + json.dumps(quantiles_jsonlike) + '''
		</script>
		'''

		div = '''
		<div id="cdf_plot"></div>
		<div id="pdf_plot"></div>

		'''

		self.plot = div+js

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

	@staticmethod
	def pretty(n):
		return np.format_float_scientific(n, precision=4)