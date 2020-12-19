from flask import Flask, render_template
from wtforms import SelectField, FloatField, FormField, BooleanField, FieldList, DecimalField
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
    family = SelectField(choices=['metalog','normal', 'lognormal', 'beta'])
    nb_pairs = SelectField('Number of P,Q pairs',choices=[i for i in range(2, 11)])

    pairs = FieldList(FormField(QuantilePairForm), min_entries=10)

    plot_custom_domain_bool = BooleanField("Specify custom domain for plot?")
    plot_custom_domain_FromTo = FormField(FromToForm)
    metalog_boundedness = BooleanField("Specify bounds for metalog?")
    metalog_lower_bound = DecimalField('Lower bound',validators=[Optional()])
    metalog_upper_bound = DecimalField('Upper bound',validators=[Optional()])
    metalog_allow_numerical = BooleanField("Allow numerical approximation if no exact metalog fit?")

    def validate(self):
        validity = True
        if not super(MyForm, self).validate():
            validity = False

        for i in range(int(self.nb_pairs.data)):
            p_or_q_missing = False
            for letter in ('P','Q'):
                if self.pairs[i][letter].data is None:
                    self.pairs[i][letter].errors.append(letter+' is required')
                    p_or_q_missing = True
            if p_or_q_missing:
                validity = False

        if self.metalog_boundedness.data:
            if self.metalog_lower_bound.data is None and self.metalog_upper_bound.data is None:
                self.metalog_boundedness.errors.append('At least one bound is required')
                validity = False

        if self.family.data == 'lognormal':
            for i in range(int(self.nb_pairs.data)):
                if self.pairs[i]['Q'].data is not None:
                    if self.pairs[i]['Q'].data <=0:
                        self.pairs[i]['Q'].errors.append("Lognormal is not defined for non-positive numbers")
                        validity = False
        return validity

    def parse_user_input(self):
        dictionary = dict(self.data)
        dictionary = self.recursively_convert_decimal_to_float(dictionary)
        nb_pairs = int(dictionary['nb_pairs'])
        dictionary['ps'] = []
        dictionary['qs'] = []
        for i in range(nb_pairs):
            p, q = dictionary["pairs"][i]['P'], dictionary["pairs"][i]['Q']
            dictionary['ps'].append(p)
            dictionary['qs'].append(q)
        return dictionary

    def recursively_convert_decimal_to_float(self,dictionary):
        for key, value in dictionary.items():
            if type(value) == decimal.Decimal:
                dictionary[key] = float(value)
            if type(value) is dict:
                self.recursively_convert_decimal_to_float(value)
        return dictionary


@app.route('/', methods=['GET'])
def show_form():
    form = MyForm()
    return render_template('index.html', form=form)


@app.route('/', methods=['POST'])
def show_result():
    form = MyForm()
    if form.validate():
        parsed_data = form.parse_user_input()
        distribution = backend.DistributionObject(parsed_data)
        try:
            plot = distribution.plot
            samples = distribution.samples
        except AttributeError:
            plot = None
            samples = None
        return render_template('index.html', form=form, plot=plot,samples=samples, distribution=distribution)
    else:
        return render_template('index.html', form=form)





if __name__ == "__main__":
    app.run(debug=True)
