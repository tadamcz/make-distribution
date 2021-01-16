from flask import Flask, render_template
from wtforms import SelectField, FloatField, FormField, BooleanField, FieldList, DecimalField, IntegerField
from wtforms.validators import Optional, number_range
from flask_wtf import FlaskForm
import mpld3
import decimal
from sigfig import round

import backend

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False  # not needed, there are no user accounts

class QuantilePairForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(QuantilePairForm, self).__init__(*args, **kwargs)
        set_render_KWs(self)

    probability_validator = number_range(min=0,max=1,message='Probabilities must be between 0 and 1')
    P = FloatField('P',validators=[Optional(),probability_validator])
    Q = FloatField('Q',validators=[Optional()])

class FromToForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(FromToForm, self).__init__(*args, **kwargs)
        set_render_KWs(self)

    From = FloatField('From',validators=[Optional()])
    To = FloatField('To',validators=[Optional()])

class DistributionForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(DistributionForm, self).__init__(*args, **kwargs)
        self.metalog_bounds.From.label = 'Lower bound'
        self.metalog_bounds.To.label = 'Upper bound'

        self.generalized_beta_bounds.From.label = 'Lower bound'
        self.generalized_beta_bounds.To.label = 'Upper bound'

        set_render_KWs(self)

    family = SelectField(choices=[('metalog','Metalog'),('normal','Normal'), ('lognormal','Lognormal'), ('beta','Beta'),('generalized_beta','Generalized Beta')])
    nb_pairs_to_display_hidden_field = IntegerField()

    pairs = FieldList(FormField(QuantilePairForm), min_entries=10)

    plot_custom_domain_bool = BooleanField("Specify custom domain for plot?")
    plot_custom_domain_FromTo = FormField(FromToForm)
    metalog_boundedness = BooleanField("Specify bounds for metalog?")
    metalog_bounds = FormField(FromToForm)
    metalog_allow_numerical = BooleanField("Allow numerical approximation if no exact metalog fit?")

    generalized_beta_bounds = FormField(FromToForm)





class MyForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        set_render_KWs(self)

    max_mixtures = 3
    distributions = FieldList(FormField(DistributionForm), min_entries=max_mixtures,max_entries=max_mixtures)
    n_distributions_to_display = IntegerField("Number of distributions_output for mixture")

    mixture_domain_for_plot_bool = BooleanField("Specify custom domain for plot?")
    mixture_domain_for_plot_FromTo = FormField(FromToForm, label='Domain for plot')
    # todo: force all plots to have same domain when mixtures are active.
    # also hide custom domain option from components when mixture is active.



    def validate(self):
        validity = True
        if not super(MyForm, self).validate():
            validity = False

        for i in range(self.n_distributions_to_display.data):
            distribution = self.distributions[i]
            for pair in distribution.pairs:
                p_or_q_missing = False
                if pair['P'].data is not None and pair['Q'].data is None:
                    pair['Q'].errors.append('Q is required')
                    p_or_q_missing = True
                if pair['P'].data is None and pair['Q'].data is not None:
                    pair['P'].errors.append('P is required')
                    p_or_q_missing = True
                if p_or_q_missing:
                    validity = False

            non_empty_pairs = 0
            for i in range(distribution.nb_pairs_to_display_hidden_field.data):
                p, q = distribution.pairs[i].P.data, distribution.pairs[i].Q.data
                if p is not None and q is not None:
                    non_empty_pairs += 1
            if non_empty_pairs < 2:
                distribution.nb_pairs_to_display_hidden_field.errors.append("At least two pairs are required")
                validity = False

            if distribution.metalog_boundedness.data:
                if distribution.metalog_bounds.From.data is None and distribution.metalog_bounds.To.data is None:
                    distribution.metalog_boundedness.errors.append('At least one bound is required')
                    validity = False

            if distribution.family.data == 'lognormal':
                for pair in distribution.pairs:
                    if pair['Q'].data is not None:
                        if pair['Q'].data <= 0:
                            pair['Q'].errors.append("Lognormal is not defined for non-positive numbers")
                            validity = False
            if distribution.family.data == 'beta':
                for pair in distribution.pairs:
                    if pair['Q'].data is not None:
                        if not 0<=pair['Q'].data <= 1:
                            pair['Q'].errors.append("Beta is defined on [0,1]. Try generalized Beta?")
                            validity = False

            if distribution.family.data == 'generalized_beta':
                if distribution.generalized_beta_bounds.From.data is None or distribution.generalized_beta_bounds.To.data is None:
                    distribution.generalized_beta_bounds.To.errors.append("Bounds are required")
                    validity = False
                else:
                    if distribution.generalized_beta_bounds.From.data > distribution.generalized_beta_bounds.To.data:
                        distribution.generalized_beta_bounds.To.errors.append("Lower bound cannot exceed upper bound")
                        validity = False
        return validity



    def parse_user_input(self):
        distributions = []
        for i in range(self.n_distributions_to_display.data):
            distribution = self.distributions[i]
            dictionary = dict(distribution.data)

            dictionary = self.recursively_convert_decimal_to_float(dictionary)
            dictionary['ps'] = []
            dictionary['qs'] = []
            dictionary['pairs_form_indices'] = []
            for j in range(distribution.nb_pairs_to_display_hidden_field.data):
                p, q = dictionary["pairs"][j]['P'], dictionary["pairs"][j]['Q']
                if p is not None:
                    dictionary['ps'].append(p)
                    dictionary['qs'].append(q)
                    dictionary['pairs_form_indices'].append(j)
            distributions.append(backend.Distribution(dictionary))

        # If mixture, set all plot domains to be the same
        if self.n_distributions_to_display.data>1:
            user_specified_domain = self.mixture_domain_for_plot_FromTo.data['From'], self.mixture_domain_for_plot_FromTo.data['To']

            if user_specified_domain != (None,None) and self.mixture_domain_for_plot_bool.data:
                min_plot, max_plot = user_specified_domain

            else:
                min_plot = min([distribution.distribution_object.ppf(0.001) for distribution in distributions])
                max_plot = max([distribution.distribution_object.ppf(1-0.001) for distribution in distributions])

            for i in range(self.n_distributions_to_display.data):
                distributions[i].plot_custom_domain = (min_plot,max_plot)

        return distributions

    def recursively_convert_decimal_to_float(self,dictionary):
        for key, value in dictionary.items():
            if type(value) == decimal.Decimal:
                dictionary[key] = float(value)
            if type(value) is dict:
                self.recursively_convert_decimal_to_float(value)
        return dictionary




def set_render_KWs(form):
    for fieldname, field in form._fields.items():
        field.render_kw = {'fieldtype': fieldname}



@app.route('/', methods=['GET'])
def getRequest():
    form = MyForm()

    # Default data
    form.n_distributions_to_display.data = 1
    for distribution in form.distributions:
        distribution.family.data = 'metalog'
        distribution.nb_pairs_to_display_hidden_field.data = 2
        distribution.metalog_allow_numerical.data = True
        distribution.pairs[0]['P'].data = .1
        distribution.pairs[0]['Q'].data = -100
        distribution.pairs[1]['P'].data = .9
        distribution.pairs[1]['Q'].data = 100

    return showResult(form)


@app.route('/', methods=['POST'])
def postRequest():
    form = MyForm()
    if form.validate():
        return showResult(form)
    else:
        return render_template('index.html', form=form, anyOutputs=False, mixture=None)

def showResult(form):
    distributions = form.parse_user_input()

    for i in range(form.n_distributions_to_display.data):
        distribution = distributions[i]
        distribution.createPlot(i)

    if form.n_distributions_to_display.data>1:
        n = form.n_distributions_to_display.data
        components = [distributions[i] for i in range(n)]
        mixture = backend.MixtureDistribution(components=components,weights=[1]*n)
        mixture.createPlot()
    else:
        mixture = None

    anyOutputs = any([d.description is not None for d in distributions])
    return render_template('index.html',
                           form=form,
                           distributions_output=distributions,
                           anyOutputs=anyOutputs,
                           mixture=mixture)



if __name__ == "__main__":
    app.run(debug=True)
