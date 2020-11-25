from flask import Flask, render_template
from wtforms import SelectField, StringField, FloatField, FormField, validators, BooleanField, FieldList, DecimalField
from wtforms.validators import  Optional, number_range
import secrets
import backend
import mpld3
import os
import decimal

from flask_wtf import FlaskForm, CSRFProtect  # Flask-WTF provides your Flask application integration with WTForms.

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False  # not needed, there are no user accounts

class QuantilePairForm(FlaskForm):
    probability_validator = number_range(min=0,max=1,message='Probabilities must be between 0 and 1')
    P = FloatField('P',validators=[Optional(),probability_validator])
    Q = FloatField('Q',validators=[Optional()])


class MyForm(FlaskForm):
    family = SelectField(choices=['metalog','normal', 'lognormal', 'beta'])
    nb_pairs = SelectField('Number of P,Q pairs',choices=[i for i in range(2, 11)])

    pairs = FieldList(FormField(QuantilePairForm), min_entries=10)

    boundedness = BooleanField("Specify bounds for metalog?")
    lower_bound = DecimalField('Lower bound',validators=[Optional()])
    upper_bound = DecimalField('Upper bound',validators=[Optional()])
    allow_lp = BooleanField("Allow linear program if no exact metalog fit?")

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

        if self.boundedness.data:
            if self.lower_bound.data is None and self.upper_bound.data is None:
                self.boundedness.errors.append('At least one bound is required')
                validity = False
        return validity


@app.route('/', methods=['GET'])
def show_form():
    form = MyForm()
    return render_template('index.html', form=form)


@app.route('/', methods=['POST'])
def show_result():
    form = MyForm()
    if form.validate():
        data = form.data
        parsed_data = parse_user_input(data)
        o = backend.DistributionObject(parsed_data)
        try:
            plot = mpld3.fig_to_html(o.plot)
            samples = o.samples
        except AttributeError:
            plot = None
            samples = None
        return render_template('index.html', form=form, plot=plot, text=o.description,samples=samples)
    else:
        return render_template('index.html', form=form)


def parse_user_input(immutable_multi_dict):
    dictionary = dict(immutable_multi_dict)
    dictionary = recursively_convert_decimal_to_float(dictionary)
    nb_pairs = int(dictionary['nb_pairs'])
    dictionary['ps'] = []
    dictionary['qs'] = []
    for i in range(nb_pairs):
        p,q = dictionary["pairs"][i]['P'],  dictionary["pairs"][i]['Q']
        dictionary['ps'].append(p)
        dictionary['qs'].append(q)
    return dictionary

def recursively_convert_decimal_to_float(dictionary):
    for key, value in dictionary.items():
        if type(value) == decimal.Decimal:
            dictionary[key] = float(value)
        if type(value) is dict:
            recursively_convert_decimal_to_float(value)
    return dictionary

if __name__ == "__main__":
    app.run(debug=True)
