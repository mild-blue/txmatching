import logging

from flask import Blueprint, render_template

logger = logging.getLogger(__name__)

template_routes = Blueprint('template_routes', __name__)


@template_routes.route('/')
def home():
    return load_patients()


@template_routes.route('/load_patients')
def load_patients():
    return render_template("load_patients.html")


@template_routes.route('/set_parameters')
def set_parameters():
    return render_template("set_parameters.html")


@template_routes.route('/set_individual')
def set_individual():
    return render_template("set_individual.html")


@template_routes.route('/solve')
def solve():
    return render_template("solve.html")


@template_routes.route('/browse_solutions')
def browse_solutions():
    return render_template("browse_solutions.html")
