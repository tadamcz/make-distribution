
import pymetalog as pm

# a list of (p,x) tuples, where P(X<x)=p
percentiles = [(0.2,8),(0.4,12),(0.5,16),(0.9,30)]

term = len(percentiles)
metalog_obj = pm.metalog(
	x = [tuple[1] for tuple in percentiles],
	probs =[tuple[0] for tuple in percentiles],
	boundedness = 'u',
	term_limit = term,
	step_len=0.001)