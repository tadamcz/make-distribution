from flask import Flask, render_template
from wtforms import SelectField, FloatField, FormField, BooleanField, FieldList, DecimalField
from wtforms.validators import Optional, number_range
from flask_wtf import FlaskForm
import mpld3
import decimal

import backend

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
        return render_template('index.html', form=form, plot=plot, text=distribution.description,samples=samples)
    else:
        return render_template('index.html', form=form)





if __name__ == "__main__":
    app.run(debug=True)
