import json
from scipy import optimize
from scipy import stats
import math
import numpy as np
import matplotlib.pyplot as plt
from metalogistic.metalogistic import MetaLogistic
import scipy.stats

mlog_lls_error_message = 'Linear least squares did not yield a valid metalog distribution for your data. ' \
						 'Things that may help: (i) allow numerical methods using the checkbox,' \
						 '(ii) add more input pairs, (iii) choose slightly different or less extreme inputs.'

mlog_any_fit_method_error_message = 'The program was not able to fit a valid metalog distribution for your data. ' \
									'Things that may help: (i) add more input pairs, (ii) choose slightly different or less extreme inputs.'

class Distribution:
	def __init__(self,dictionary):
		self.samples = None
		self.description = []
		self.errors = []

		self.dictionary = dictionary
		self.family = dictionary['family']
		self.ps = dictionary['ps']
		self.qs = dictionary['qs']
		self.pairs_form_indices = dictionary['pairs_form_indices']

		self.n_points_to_plot = 200


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
				self.description.append('More than two quantiles provided: least squares fit.')

				mu_init, sigma_init = self.initial_guess_params()

				fit = optimize.curve_fit(
					lambda x, mu, sigma: stats.norm(mu, sigma).cdf(x),
					xdata=self.qs,
					ydata=self.ps,
					p0=[mu_init, sigma_init]
				)

				(mu, sigma), covariances = fit
				mu_sd, sigma_sd = np.sqrt(np.diag(covariances))

				self.description.append('mu: ' + self.pretty(mu))
				self.description.append('sigma: ' + self.pretty(sigma))

			self.distribution_object = scipy.stats.norm(loc=mu, scale=sigma)

		if self.family == 'lognormal':
			self.description.append('Log-normal distribution')
			qs_log_transformed = [math.log(x) for x in self.qs]
			if len(self.ps) == 2:
				self.description.append('Two quantiles provided, using exact fit.')
				mu, sigma = self.normal_parameters(qs_log_transformed[0], self.ps[0], qs_log_transformed[1], self.ps[1])

				self.description.append('mu: ' + self.pretty(mu))
				self.description.append('sigma: ' + self.pretty(sigma))

			if len(self.ps) > 2:
				self.description.append('More than two quantiles provided: least squares fit.')
				mu_init, sigma_init = self.initial_guess_params(self.ps, qs_log_transformed)

				fit = optimize.curve_fit(
					lambda x, mu, sigma: stats.lognorm(s=sigma, scale=math.exp(mu)).cdf(x),
					xdata=self.qs,
					ydata=self.ps,
					p0=[mu_init, sigma_init]
				)

				(mu, sigma), covariances = fit
				mu_sd, sigma_sd = np.sqrt(np.diag(covariances))
				self.description.append('mu: ' + self.pretty(mu))
				self.description.append('sigma: ' + self.pretty(sigma))

			self.distribution_object = scipy.stats.lognorm(s=sigma, scale=math.exp(mu))

		if self.family == 'beta':
			for q in self.qs:
				if not 0 <= q <= 1:
					self.errors.append("Quantiles out of bounds. Beta distribution defined on [0,1]")
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

			self.description.append('Beta distribution: least squares fit.')
			self.description.append('alpha: ' + self.pretty(alpha))
			self.description.append('beta: ' + self.pretty(beta))

			self.distribution_object = scipy.stats.beta(alpha, beta)

		if self.family == 'generalized_beta':
			self.generalized_beta_lbound, self.generalized_beta_ubound = self.dictionary['generalized_beta_bounds']['From'], self.dictionary['generalized_beta_bounds']['To']

			loc = self.generalized_beta_lbound
			scale = self.generalized_beta_ubound - loc

			alpha_init, beta_init = 1, 1

			fit = optimize.curve_fit(
				lambda x, alpha, beta: stats.beta(alpha, beta, loc=loc, scale=scale).cdf(x),
				xdata=self.qs,
				ydata=self.ps,
				p0=[alpha_init, beta_init]
			)

			(alpha, beta), covariances = fit

			self.description.append('Generalized beta distribution: least squares fit.')
			self.description.append('alpha: ' + self.pretty(alpha))
			self.description.append('beta: ' + self.pretty(beta))

			self.distribution_object = scipy.stats.beta(alpha, beta, loc=loc, scale=scale)
			self.distribution_object.a = self.generalized_beta_lbound
			self.distribution_object.b = self.generalized_beta_ubound



		# self.generatePlotDataSciPy()

	def initMetalog(self):
		self.n_samples = 5000
		self.description.append('Meta-logistic distribution.')

		self.metalog_boundedness = self.dictionary['metalog_boundedness']

		if self.metalog_boundedness:
			self.metalog_lower_bound, self.metalog_upper_bound = self.dictionary['metalog_bounds']['From'],self.dictionary['metalog_bounds']['To']
		else:
			self.metalog_lower_bound, self.metalog_upper_bound = None, None

		if self.dictionary['metalog_allow_numerical']:
			self.metalog_fit_method = None
		else:
			self.metalog_fit_method = 'Linear least squares'

		try:
			self.distribution_object = MetaLogistic(self.ps, self.qs,
													lbound=self.metalog_lower_bound,
													ubound=self.metalog_upper_bound,
													fit_method=self.metalog_fit_method)
		except TimeoutError:
			self.errors.append("Timed out while attempting to fit distribution.")
			return
		except Exception as mlog_exception:
			self.errors.append(mlog_exception)
			return

		if not self.distribution_object.valid_distribution:
			if self.dictionary['metalog_allow_numerical']:
				self.errors.append(mlog_any_fit_method_error_message)
			else:
				self.errors.append(mlog_lls_error_message)
		self.description.append('Fit method: ' + self.distribution_object.fit_method_used)
		# self.generatePlotDataMetalog()
		self.samples = np.array2string(self.distribution_object.rvs(size=self.n_samples).flatten(),
									   separator=', ',
									   threshold=self.n_samples + 1,
									   max_line_width=float('inf'))


	def generatePlotDataSciPy(self):
		if self.plot_custom_domain:
			left, right = self.plot_custom_domain

		else:
			y_bound = 0.001
			left = self.distribution_object.ppf(y_bound)
			right = self.distribution_object.ppf(1 - y_bound)

			if min(self.qs)<left:
				left = min(self.qs)
			if max(self.qs)>right:
				right = max(self.qs)

		self.x_axis = np.linspace(left,right,self.n_points_to_plot)

		self.y_axis_cdf = self.distribution_object.cdf(self.x_axis)
		self.y_axis_pdf = self.distribution_object.pdf(self.x_axis)

		self.x_axis_pdf = self.x_axis
		self.x_axis_cdf = self.x_axis

	def generatePlotDataMetalog(self):
		if self.plot_custom_domain:
			left, right = self.plot_custom_domain
			left, right = self.intersect_intervals([(left,right), (self.distribution_object.a, self.distribution_object.b)])

			cdf_data = self.distribution_object.createCDFPlotData(x_from_to=(left, right), n=self.n_points_to_plot)
			pdf_data = self.distribution_object.createPDFPlotData(x_from_to=(left, right), n=self.n_points_to_plot)
		else:
			cdf_data = self.distribution_object.createCDFPlotData(n=self.n_points_to_plot)
			pdf_data = self.distribution_object.createPDFPlotData(n=self.n_points_to_plot)

		self.x_axis_cdf = cdf_data['X-values']
		self.y_axis_cdf = cdf_data['Probabilities']

		self.x_axis_pdf = pdf_data['X-values']
		self.y_axis_pdf = pdf_data['Densities']

		if min(self.y_axis_pdf<0):
			if self.dictionary['metalog_allow_numerical']:
				self.errors.append(mlog_any_fit_method_error_message)
			else:
				self.errors.append(mlog_lls_error_message)

	def generatePlotData(self):
		if self.family == 'metalog':
			self.generatePlotDataMetalog()
		else:
			self.generatePlotDataSciPy()

	def createPlot(self, plotIndex):
		self.generatePlotData()
		cdf_jsonlike = [{'x': self.x_axis_cdf[i], 'y': self.y_axis_cdf[i]} for i in range(len(self.x_axis_cdf))]
		pdf_jsonlike = [{'x': self.x_axis_pdf[i], 'y': self.y_axis_pdf[i]} for i in range(len(self.x_axis_pdf))]

		quantiles_jsonlike = [{'x': self.qs[i], 'y': self.ps[i]} for i in range(len(self.qs))]

		cdf_metadata_jsonlike = dict(xmin=min(self.x_axis_cdf), ymin=min(self.y_axis_cdf), xmax=max(self.x_axis_cdf), ymax=max(self.y_axis_cdf))
		pdf_metadata_jsonlike = dict(xmin=min(self.x_axis_pdf), ymin=min(self.y_axis_pdf), xmax=max(self.x_axis_pdf), ymax=max(self.y_axis_pdf))

		maximum_density_to_display = min(np.percentile(self.y_axis_pdf, 80)*5,max(self.y_axis_pdf))


		plot_data_dict = {
			'cdf_data': cdf_jsonlike,
			'cdf_metadata': cdf_metadata_jsonlike,
			'pdf_data': pdf_jsonlike,
			'pdf_metadata': pdf_metadata_jsonlike,
			'quantiles': quantiles_jsonlike,
			'maximum_density_to_display': maximum_density_to_display,
			'pairs_form_indices': self.pairs_form_indices,
			'lbound': self.distribution_object.a,
			'ubound': self.distribution_object.b,
			}


		js = '<script>plotData['+str(plotIndex)+'] = '+json.dumps(plot_data_dict)+'</script>'


		divcdf = '<div id="cdf_plot'+str(plotIndex)+'"></div>'
		divpdf = '<div id="pdf_plot'+str(plotIndex)+'"></div>'


		self.plot = divcdf+divpdf+js

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
			raise ValueError("the distributions_output have no overlap")

		intersect_left, intersect_right = max(interval1_left, interval2_left), min(interval1_right, interval2_right)

		return intersect_left, intersect_right

class MixtureDistribution(stats.rv_continuous):
	def __init__(self, components,weights):
		super().__init__()
		self.components = components
		self.weights = np.asarray(weights)
		self.n_components = len(weights)

		self.createPlot()

	def _cdf(self, x):
		component_cdfs = [c.distribution_object.cdf(x) for c in self.components]
		return np.average(component_cdfs,weights=self.weights)

	def _pdf(self, x):
		component_pdfs = [c.distribution_object.cdf(x) for c in self.components]
		return np.average(component_pdfs,weights=self.weights)

	def _rvs(self, size=1, random_state=None):
		samples = []
		for c in self.components:
			samples.append(c.distribution_object.rvs(size=size/self.n_components))
		return samples

	def generatePlotData(self):
		n_points_to_plot = self.components[0].n_points_to_plot  # arbitrarily choose the first one
		left, right = self.components[0].plot_custom_domain

		self.x_axis_cdf, self.x_axis_pdf = (np.linspace(left,right,n_points_to_plot),)*2

		cdf_matrix_to_average = np.empty(shape=(0,n_points_to_plot))
		pdf_matrix_to_average = np.empty(shape=(0,n_points_to_plot))
		for i,c in enumerate(self.components):

			if c.family == 'metalog':
				cdf_matrix_to_average = np.vstack((cdf_matrix_to_average,
												   c.distribution_object.cdf(self.x_axis_cdf)))

				pdf_matrix_to_average = np.vstack((pdf_matrix_to_average,
												   c.distribution_object.pdf(self.x_axis_pdf)))
			else:
				cdf_matrix_to_average = np.vstack((cdf_matrix_to_average,
												   c.y_axis_cdf))

				pdf_matrix_to_average = np.vstack((pdf_matrix_to_average,
												   c.y_axis_pdf))

		self.y_axis_cdf = np.average(cdf_matrix_to_average,weights=self.weights,axis=0)
		self.y_axis_pdf = np.average(pdf_matrix_to_average,weights=self.weights,axis=0)


	def createPlot(self):
		self.generatePlotData()
		cdf_jsonlike = [{'x': self.x_axis_cdf[i], 'y': self.y_axis_cdf[i]} for i in range(len(self.x_axis_cdf))]
		pdf_jsonlike = [{'x': self.x_axis_pdf[i], 'y': self.y_axis_pdf[i]} for i in range(len(self.x_axis_pdf))]

		cdf_metadata_jsonlike = dict(xmin=min(self.x_axis_cdf), ymin=min(self.y_axis_cdf), xmax=max(self.x_axis_cdf), ymax=max(self.y_axis_cdf))
		pdf_metadata_jsonlike = dict(xmin=min(self.x_axis_pdf), ymin=min(self.y_axis_pdf), xmax=max(self.x_axis_pdf), ymax=max(self.y_axis_pdf))

		maximum_density_to_display = min(np.percentile(self.y_axis_pdf, 80) * 5, max(self.y_axis_pdf))

		plot_data_dict = {
			'cdf_data': cdf_jsonlike,
			'cdf_metadata': cdf_metadata_jsonlike,
			'pdf_data': pdf_jsonlike,
			'pdf_metadata': pdf_metadata_jsonlike,
			'maximum_density_to_display': maximum_density_to_display,
		}

		js = '<script>mixturePlotData = ' + json.dumps(plot_data_dict) + '</script>'

		divcdf = '<div id="mixture_cdf_plot"></div>'
		divpdf = '<div id="mixture_pdf_plot"></div>'

		self.plot = divcdf+divpdf+js
