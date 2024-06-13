#!/usr/bin/env python3
"""
simple flask app
"""
from flask import Flask, jsonify, request, abort, redirect
from auth import Auth


AUTH = Auth()
app = Flask(__name__)


@app.route("/")
def index():
    ''' first route'''
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def users():
    ''' second route'''
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        user = AUTH.register_user(email, password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400
    return jsonify({"email": user.email, "message": "user created"})


@app.route("/sessions", methods=["POST"])
def login():
    ''' third route'''
    email = request.form.get("email")
    password = request.form.get("password")
    user = AUTH.valid_login(email, password)
    if not user:
        abort(401)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", AUTH.create_session(email))
    return response


@app.route("/sessions", methods=["DELETE"])
def logout():
    ''' fourth route '''
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect('/')


@app.route("/profile")
def profile():
    ''' fifth route '''
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if not user:
        abort(403)
    return jsonify({"email": user.email})


@app.route("/reset_password", methods=["POST"])
def get_reset_password_token():
    ''' sixth route '''
    email = request.form.get("email")
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "reset_token": reset_token})


@app.route("/reset_password", methods=["PUT"])
def update_password():
    ''' sixth route '''
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "message": "Password updated"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
