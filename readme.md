* Provide points on the cumulative distribution function, and this script will find the the distribution that fits them best.
It will return a graph, the distribution's parameters, and some commonly-used quantiles.
* Supports the innovative and highly flexible metalog family of distributions.
* [In-depth explanatory blog post](https://fragile-credences.github.io/quantiles/)
* [Run it in your browser](https://colab.research.google.com/drive/1YfS9JUMdXpilfxcgWwZUMvyRSKWrXxRE)
* _Webapps_: Currently you must use separate webapps [for traditional distributions](https://quantile-elicitor.herokuapp.com/) and for [the metalog distribution](https://tmkadamcz.shinyapps.io/metalog/). The traditional distributions webapp is in Python and based on the `develop` branch of this repository. The metalog distribution webapp is a R Shiny app, and its code is in [another repository](https://github.com/tmkadamcz/metalog-rshiny).

# Example usage
## input
```python
################################
### Enter values below ===> ####
################################

# Instructions:
# Choose a distribution family.
# Provide quantiles for the distribution

# family can be 'normal', 'lognormal', 'metalog'
family = 'lognormal'

# Bounds for metalog
# The metalog distribution can be unbounded, or bounded to the left, or the right, or both
# Specify between 0 and 2 bounds, leaving the others as None
metalog_leftbound = None
metalog_rightbound = None

# a list of (p,x) tuples, where P(X<x)=p
# (If you provide more than two quantiles for a 2-parameter distribution.
# least squares will be used for fitting. You may provide unlimited
# quantiles for the metalog distribution)'''
quantiles = [(0.1,50),(0.5,70),(0.75,100),(0.9,150)]

# list of quantiles to print
quantiles_out = [0.01,0.1,0.25,0.5,0.75,0.9,0.99]

# Override defaults for domain to plot?
# example: domain_override = [-50,100]
domain_override = None

################################
### <=== Enter values above ####
################################
```
## Output
```python
More than two quantiles provided, using least squares fit
Lognormal distribution
mu 4.313122980928514
sigma 0.409687416531683
quantiles:
0.01 28.79055927521217
0.1 44.17183774344628
0.25 56.64439363937313
0.5 74.67332855521319
0.75 98.44056294458953
0.9 126.2366766332274
0.99 193.67827989071688
```
![](https://fragile-credences.github.io/images/quantiles/lognormal.png)

