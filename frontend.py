from flask import Flask, render_template
from wtforms import SelectField, StringField, FloatField, FormField, validators, BooleanField
import backend
import mpld3
import os

from flask_wtf import FlaskForm, CSRFProtect  # Flask-WTF provides your Flask application integration with WTForms.

app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = os.environ['csrf']

class QuantilePairForm(FlaskForm):
    p = FloatField('P')
    q = FloatField('Q')


class MyForm(FlaskForm):
    family = SelectField(choices=['metalog', 'normal', 'lognormal', 'beta'])
    nb_pairs = SelectField(choices=[i for i in range(2, 11)])

    pair1 = FormField(QuantilePairForm)
    pair2 = FormField(QuantilePairForm)
    pair3 = FormField(QuantilePairForm)
    pair4 = FormField(QuantilePairForm)
    pair5 = FormField(QuantilePairForm)


@csrf.exempt  # I believe we don't need CSRF for a site without any user accounts
@app.route('/', methods=['GET'])
def show_form():
    form = MyForm()
    return render_template('index.html', form=form)


@csrf.exempt  # I believe we don't need CSRF for a site without any user accounts
@app.route('/', methods=['POST'])
def show_result():
    form = MyForm()
    data = form.data
    parsed_data = parse_user_input(data)
    graph,text = backend.main(parsed_data)
    graph = mpld3.fig_to_html(graph)
    return render_template('index.html', form=form, graph=graph, text=text)


def parse_user_input(immutable_multi_dict):
    dictionary = dict(immutable_multi_dict)
    family = dictionary['family']
    nb_pairs = int(dictionary['nb_pairs'])
    pairs = []
    for i in range(1, nb_pairs + 1):
        pairs.append((dictionary["pair" + str(i)]["p"], dictionary["pair" + str(i)]["q"]))
    return {"family": family, "pairs": pairs}

if __name__ == "__main__":
    app.run(debug=True)
