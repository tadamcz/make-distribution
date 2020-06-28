Provide percentiles, and this script will find the the distribution that fits them best.
It will give you the distribution's parameters and some lodestar percentiles.

(For completeness, you can also do the reverse: supply the parameters and obtain lodestar percentiles)

Run it in your browser: https://colab.research.google.com/drive/1YfS9JUMdXpilfxcgWwZUMvyRSKWrXxRE

# Example usage
## input
```python
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
```
## Output
```python
More than two percentiles provided, using least squares fit
Lognormal distribution
mu 4.305985861552688
sigma 0.4527404563264039
Percentiles:
0.01 25.861466048620933
0.1 41.50341117979741
0.25 54.631850997030796
0.5 74.14227345121989
0.75 100.62036361927821
0.9 132.44879291250342
0.99 212.55858821695062
```