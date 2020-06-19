from scipy import stats
import math

################################
### Enter values below ===> ####
################################

# Instructions: you must provide either a 95% CI, or an estimate and one of p and standard error.

# Estimated quantity
estimate = None

# Value of estimate under null hypothesis. Typically 0.
# Example: estimate_null_value = 42
estimate_null_value = 0

# 95% confidence interval. Two values separated by commas (a tuple).
# Example: ci95 = 0.3,2
ci95 = None

# p-value for the hypothesis that estimate=estimate_null_value
# Example: p = 0.01
p = None

# Standard error of estimated quantity
# Example: standard_error = 1
standard_error = None

# Set to True if your estimate is a ratio.
is_ratio = False
# This will cause everything to be evaluated on the log scale,
# and exponentiated back before being returned by the program.
# Although the estimate of the ratio has an asymptotically normal
# distribution around the true ratio (via taking logs and using the delta method),
# the log of a ratio converges to normality much faster.


################################
### <=== Enter values above ####
################################











#### Checks
p_or_se = not(p is None and standard_error is None)

if ci95 is None and (estimate is None or p_or_se is False):
	raise ValueError("You must provide either a 95% CI, or an estimate and one of p and standard error")

if [p,standard_error,ci95].count(None)<2:
	raise ValueError("You must provide at most one of p, standard error, and 95% CI")

if [ci95,estimate].count(None)<1:
	raise ValueError("You cannot provide both an estimate and a 95% CI")

if is_ratio and standard_error is not None:
	raise ValueError('''Supplying a standard error for a ratio is not supported.
     Supply a p-value or a 95% CI instead.''')


#### Math

# Define left,right of CI
if ci95 is not None:
	ci95_left, ci95_right = ci95
else:
	ci95_left,ci95_right=None,None

# Actual math
if is_ratio:
	if ci95 is not None:
		ci95_left,ci95_right=math.log(ci95_left),math.log(ci95_right)
	if estimate is not None:
		estimate = math.log(estimate)

if ci95 is not None:
	width = ci95_right-ci95_left
	standard_error = (width/2)/1.96
	estimate = (ci95_left+ci95_right)/2
	z = (estimate-estimate_null_value)/standard_error
	p = 2*stats.norm.cdf(-abs(z))

else:
	if p is not None:
		z =  stats.norm.ppf(p/2,loc=estimate_null_value) #could use t distribution instead, but this would require knowing the df
		standard_error = abs(estimate/z)

	if standard_error is not None:
		z = (estimate-estimate_null_value)/standard_error
		p = 2*stats.norm.cdf(-abs(z))

	ci95_left,ci95_right = estimate-1.96*standard_error, estimate+1.96*standard_error


if is_ratio:
	estimate = math.exp(estimate)
	ci95_left,ci95_right=math.exp(ci95_left),math.exp(ci95_right)


# Print output
print_width = 20

print('estimate'.ljust(print_width),estimate)
print('estimate_null_value'.ljust(print_width),estimate_null_value)
print('ci95_left'.ljust(print_width),ci95_left)
print('ci95_right'.ljust(print_width),ci95_right)
print('p-value'.ljust(print_width),p)
print('z-score'.ljust(print_width),z)
print('standard_error'.ljust(print_width),standard_error)