from flask import jsonify


def response_ok(data):
    return jsonify(data)
