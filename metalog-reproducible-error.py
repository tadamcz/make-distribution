from metalog import metalog

# a list of (p,x) tuples, where P(X<x)=p
percentiles = [(0.1,0),
			   (0.2,50),
			   (0.3,51)]

term = len(percentiles)

metalog_obj = metalog.fit(
		x = [tuple[1] for tuple in percentiles],
		probs =[tuple[0] for tuple in percentiles],
		boundedness = 'u',
		term_limit = term,
		step_len=0.01)

domain_for_debugging = [i for i in range(100)]
pdf_values = metalog.d(metalog_obj,domain_for_debugging,term=term)
if len(pdf_values)!=len(domain_for_debugging):
    raise RuntimeError("dmetalog gave",len(pdf_values),"results, instead of",len(domain_for_debugging))

cdf_values = metalog.p(metalog_obj,domain_for_debugging,term=term)
if len(cdf_values)!=len(domain_for_debugging):
    raise RuntimeError("dmetalog gave",len(cdf_values),"results, instead of",len(domain_for_debugging))