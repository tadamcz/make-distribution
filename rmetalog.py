import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

# import R's utility package
utils = rpackages.importr('utils')

# select a mirror for R packages
utils.chooseCRANmirror(ind=1) # select the first mirror in the list

# install and import rmetalog
utils.install_packages('rmetalog')
rpackages.importr('rmetalog')

# a list of (p,x) tuples, where P(X<x)=p
percentiles = [(0.1,0),
			   (0.2,50),
			   (0.5,70)]

term = len(percentiles)
step_len = 0.001

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

r_x = robjects.FloatVector([q for p,q in percentiles])
r_probs = robjects.FloatVector([p for p,q in percentiles])
boundedness = 'u'
r_term_limit = robjects.FloatVector([term])
r_step_len = robjects.FloatVector([step_len])


r_metalog_obj = r_metalog_func(x=r_x,probs=r_probs,boundedness=boundedness,term_limit=r_term_limit,step_len=r_step_len)

r_domain = robjects.FloatVector([i for i in range(100)])

cdf_values = r_pmetalog_func(metalog_obj=r_metalog_obj,q=r_domain,term=r_term_limit)
pdf_values = r_dmetalog_func(metalog_obj=r_metalog_obj,q=r_domain,term=r_term_limit)