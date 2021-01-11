import json
from scipy import optimize
from scipy import stats
import math
import numpy as np
import matplotlib.pyplot as plt
from metalogistic.metalogistic import MetaLogistic
import scipy.stats

class DistributionObject:
	def __init__(self,dictionary):
		self.samples = None
		self.description = []
		self.errors = []

		self.dictionary = dictionary
		self.family = dictionary['family']
		self.ps = dictionary['ps']
		self.qs = dictionary['qs']

		self.plot_custom_domain = False
		if dictionary['plot_custom_domain_bool']:
			self.plot_custom_domain = (dictionary['plot_custom_domain_FromTo']['From'],dictionary['plot_custom_domain_FromTo']['To'])


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
		self.n_samples = 5000
		self.description.append('Meta-logistic distribution.')
		term = len(self.ps)

		self.metalog_boundedness = self.dictionary['metalog_boundedness']

		if self.metalog_boundedness:
			self.metalog_lower_bound, self.metalog_upper_bound = self.dictionary['metalog_lower_bound'], self.dictionary['metalog_upper_bound']
		else:
			self.metalog_lower_bound, self.metalog_upper_bound = None, None

		if self.dictionary['metalog_allow_numerical']:
			self.metalog_fit_method = None
		else:
			self.metalog_fit_method = 'Linear least squares'

		try:
			self.metalog_object = MetaLogistic(self.ps,self.qs,
											   lbound=self.metalog_lower_bound,
											   ubound=self.metalog_upper_bound,
											   fit_method=self.metalog_fit_method)
		except TimeoutError:
			self.errors.append("Timed out while attempting to fit distribution.")
			return
		except Exception as mlog_exception:
			self.errors.append(mlog_exception)
			return

		if not self.metalog_object.valid_distribution:
			if self.dictionary['metalog_allow_numerical']:
				self.errors.append('The program was not able to fit a valid metalog distribution for your data. Things that may help: (i) add more input pairs, (ii) choose less extreme inputs.')
			else:
				self.errors.append('Linear least squares did not yield a valid metalog distribution for your data. Things that may help: (i) allow numerical methods using the checkbox, (ii) add more input pairs, (iii) choose less extreme inputs.')
		self.description.append('Fit method: ' + self.metalog_object.fit_method_used)
		self.generatePlotDataMetalog()
		self.createPlot()
		self.samples = np.array2string(self.metalog_object.rvs(size=self.n_samples).flatten(),
									   separator=', ',
									   threshold=self.n_samples + 1,
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

		self.x_axis_pdf = self.x_axis
		self.x_axis_cdf = self.x_axis

	def generatePlotDataMetalog(self):
		number_points = 300
		if self.plot_custom_domain:
			left, right = self.plot_custom_domain
			left, right = self.intersect_intervals([(left,right),(self.metalog_object.a, self.metalog_object.b)])

			cdf_data = self.metalog_object.createCDFPlotData(x_from_to=(left, right), n=number_points)
			pdf_data = self.metalog_object.createPDFPlotData(x_from_to=(left, right), n=number_points)
		else:
			cdf_data = self.metalog_object.createCDFPlotData(n=number_points)
			pdf_data = self.metalog_object.createPDFPlotData(n=number_points)

		self.x_axis_cdf = cdf_data['X-values']
		self.y_axis_cdf = cdf_data['Probabilities']

		self.x_axis_pdf = pdf_data['X-values']
		self.y_axis_pdf = pdf_data['Densities']


	def createPlot(self):
		cdf_jsonlike = [{'x': self.x_axis_cdf[i], 'y': self.y_axis_cdf[i]} for i in range(len(self.x_axis_cdf))]
		pdf_jsonlike = [{'x': self.x_axis_pdf[i], 'y': self.y_axis_pdf[i]} for i in range(len(self.x_axis_pdf))]

		quantiles_jsonlike = [{'x': self.qs[i], 'y': self.ps[i]} for i in range(len(self.qs))]

		cdf_metadata_jsonlike = dict(xmin=min(self.x_axis_cdf), ymin=min(self.y_axis_cdf), xmax=max(self.x_axis_cdf), ymax=max(self.y_axis_cdf))
		pdf_metadata_jsonlike = dict(xmin=min(self.x_axis_pdf), ymin=min(self.y_axis_pdf), xmax=max(self.x_axis_pdf), ymax=max(self.y_axis_pdf))

		maximum_density_to_display = min(np.median(self.y_axis_pdf)*50,max(self.y_axis_pdf))




		js = '''
		<script>
		const cdf_data =''' + json.dumps(cdf_jsonlike) + '''
		const cdf_metadata =''' + json.dumps(cdf_metadata_jsonlike) + '''
		const pdf_data =''' + json.dumps(pdf_jsonlike) + '''
		const pdf_metadata =''' + json.dumps(pdf_metadata_jsonlike) + '''
		const quantiles =''' + json.dumps(quantiles_jsonlike) + '''
		const maximum_density_to_display=''' +str(maximum_density_to_display) + '''
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

	@staticmethod
	def intersect_intervals(two_tuples):
		interval1, interval2 = two_tuples

		interval1_left, interval1_right = interval1
		interval2_left, interval2_right = interval2

		if interval1_right < interval2_left or interval2_right < interval2_left:
			raise ValueError("the distributions have no overlap")

		intersect_left, intersect_right = max(interval1_left, interval2_left), min(interval1_right, interval2_right)

		return intersect_left, intersect_right