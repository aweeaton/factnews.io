from datetime import date

import boto3
from flask import Flask
from flask import request, render_template, redirect, \
    url_for, flash, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user
import requests
import os
from app import application, classes, db, sift, credibility_model


@application.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(application.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon')


@application.route('/')
def search():
    """Search page"""
    return render_template('search_page.html',
                           authenticated_user=current_user.is_authenticated)


@application.route('/', methods=['POST', 'GET'])
def search_post():
    """Results page"""
    url = request.form['url']
    if url[0:4].lower() != "http":
        url = "https://" + url
    try:
        status_code = requests.get(url).status_code
        if status_code != 200:
            flash("Invalid URL or site may require membership")
            return render_template('search_page.html')
    except (requests.exceptions.ConnectionError,
            requests.exceptions.MissingSchema):
        if len(url) == 0:
            return render_template('search_page.html')
        flash("Invalid URL or site may require membership")
        return render_template('search_page.html')

    title, summary, encoded_txt = sift.retrieve_article_details(url)
    search_q, search_q_google = sift.trace_claim(url)
    wiki_link, about_src, source_wiki, source_about = sift.investigate_source(
        url)
    if len(source_wiki) < 250:
        source_wiki = "\"" + source_wiki[:250] + "\""
    else:
        source_wiki = "\"" + source_wiki[:250] + "...\""
    if len(source_about) < 250:
        source_about = "\"" + source_about[:250] + "\""
    else:
        source_about = "\"" + source_about[:250] + "...\""
    top_5_results, query_page = sift.find_better_coverage(url)
    sentiment = credibility_model.sentiment(encoded_txt)
    output = {
        'url': url,
        'title': title,
        'summary': summary,
        'source': sift.reveal_source(url)[1],
        'credibility_score': credibility_model.predict_credibility(
            encoded_txt),
        'trace_created': "March 30/ 2020",
        'trace_link': "fakeWebsite/newsrelated",
        'search_q': search_q,
        'search_q_google': search_q_google,
        'source_about': source_about,
        'source_wiki': source_wiki,
        'top_5_results': top_5_results,
        'query_page': query_page,
        'wiki_link': wiki_link,
        'about_src': about_src,
        'sentiment': sentiment
    }
    return render_template('results_page.html', output=output,
                           authenticated_user=current_user.is_authenticated,
                           today=date.today())


@application.route('/model_page')
def model_page():
    """Model explanation page"""
    return render_template('model_page.html',
                           authenticated_user=current_user.is_authenticated)


@application.route('/register', methods=('GET', 'POST'))
def register():
    """Registration Page"""
    registration_form = classes.RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data
        email = registration_form.email.data

        user = classes.User(username, email, password)
        msg = classes.UserBL.RegisterUserDB(user)

        if msg == "User registered":
            return redirect(url_for('login'))
        else:
            if msg == "Email address already taken":
                flash(msg + ": " + email)
            if msg == "Username already taken":
                flash(msg + ": " + username)

            return render_template(
                'register.html',
                form=registration_form,
                authenticated_user=current_user.is_authenticated)

    return render_template('register.html', form=registration_form,
                           authenticated_user=current_user.is_authenticated)


@application.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    login_form = classes.LogInForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        # Look for user in the database
        user = classes.User.query.filter_by(username=username).first()
        # Display invalid login if data is invalid
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return render_template('login.html', form=login_form)
        # Login and validate the user if correct login data
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for("search"))
    return render_template('login.html', form=login_form,
                           authenticated_user=current_user.is_authenticated)


@application.route('/logout')
@login_required
def logout():
    """Logout page"""
    logout_user()
    return redirect(url_for('search'))


@application.route('/about', methods=['GET', 'POST'])
def about():
    """About Page"""
    return render_template('jumbo.html',
                           authenticated_user=current_user.is_authenticated)
