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
    probability_validator = number_range(min=0,max=1,message='Probabilities must be between 0 and 1')
    P = FloatField('P',validators=[Optional(),probability_validator])
    Q = FloatField('Q',validators=[Optional()])

class FromToForm(FlaskForm):
    From = FloatField('From',validators=[Optional()])
    To = FloatField('To',validators=[Optional()])

class MyForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.metalog_bounds.From.label = 'Lower bound'
        self.metalog_bounds.To.label = 'Upper bound'

        self.generalized_beta_bounds.From.label = 'Lower bound'
        self.generalized_beta_bounds.To.label = 'Upper bound'

    family = SelectField(choices=[('metalog','Metalog'),('normal','Normal'), ('lognormal','Lognormal'), ('beta','Beta'),('generalized_beta','Generalized Beta')])
    nb_pairs_to_display_hidden_field = IntegerField()

    pairs = FieldList(FormField(QuantilePairForm), min_entries=10)

    plot_custom_domain_bool = BooleanField("Specify custom domain for plot?")
    plot_custom_domain_FromTo = FormField(FromToForm)
    metalog_boundedness = BooleanField("Specify bounds for metalog?")
    metalog_bounds = FormField(FromToForm)
    metalog_allow_numerical = BooleanField("Allow numerical approximation if no exact metalog fit?")

    generalized_beta_bounds = FormField(FromToForm)

    def validate(self):
        validity = True
        if not super(MyForm, self).validate():
            validity = False

        for pair in self.pairs:
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
        for i in range(self.nb_pairs_to_display_hidden_field.data):
            p, q = self.pairs[i].P.data, self.pairs[i].Q.data
            if p is not None and q is not None:
                non_empty_pairs += 1
        if non_empty_pairs<2:
            self.nb_pairs_to_display_hidden_field.errors.append("At least two pairs are required")
            validity = False


        if self.metalog_boundedness.data:
            if self.metalog_bounds.From.data is None and self.metalog_bounds.To.data is None:
                self.metalog_boundedness.errors.append('At least one bound is required')
                validity = False

        if self.family.data == 'lognormal':
            for pair in self.pairs:
                if pair['Q'].data is not None:
                    if pair['Q'].data <=0:
                        pair['Q'].errors.append("Lognormal is not defined for non-positive numbers")
                        validity = False
        if self.family.data == 'generalized_beta':
            if self.generalized_beta_bounds.From.data is None or self.generalized_beta_bounds.To.data is None:
                self.generalized_beta_bounds.To.errors.append("Bounds are required")
                validity = False
            else:
                if self.generalized_beta_bounds.From.data > self.generalized_beta_bounds.To.data:
                    self.generalized_beta_bounds.To.errors.append("Lower bound cannot exceed upper bound")
                    validity = False
        return validity

    def parse_user_input(self):
        dictionary = dict(self.data)
        dictionary = self.recursively_convert_decimal_to_float(dictionary)
        dictionary['ps'] = []
        dictionary['qs'] = []
        dictionary['pairs_form_indices'] = []
        for i in range(dictionary['nb_pairs_to_display_hidden_field']):
            p, q = dictionary["pairs"][i]['P'], dictionary["pairs"][i]['Q']
            if p is not None:
                dictionary['ps'].append(p)
                dictionary['qs'].append(q)
                dictionary['pairs_form_indices'].append(i)
        return dictionary

    def recursively_convert_decimal_to_float(self,dictionary):
        for key, value in dictionary.items():
            if type(value) == decimal.Decimal:
                dictionary[key] = float(value)
            if type(value) is dict:
                self.recursively_convert_decimal_to_float(value)
        return dictionary


@app.route('/', methods=['GET'])
def getRequest():
    form = MyForm()

    # Default data
    form.family.data = 'metalog'
    form.nb_pairs_to_display_hidden_field.data = 2
    form.metalog_allow_numerical.data = True
    form.pairs[0]['P'].data = .1
    form.pairs[0]['Q'].data = -100
    form.pairs[1]['P'].data = .9
    form.pairs[1]['Q'].data = 100

    return showResult(form)


@app.route('/', methods=['POST'])
def postRequest():
    form = MyForm()
    if form.validate():
        return showResult(form)
    else:
        return render_template('index.html', form=form)

def showResult(form):
    parsed_data = form.parse_user_input()
    distribution = backend.DistributionObject(parsed_data)
    try:
        plot = distribution.plot
        samples = distribution.samples
    except AttributeError:
        plot = None
        samples = None
    return render_template('index.html', form=form, plot=plot, samples=samples, distribution=distribution)



if __name__ == "__main__":
    app.run(debug=True)
