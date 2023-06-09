from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
# from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "TopSecret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)

with app.app_context():
    db.create_all()


# ______________________ User Routes ______________________


@app.route('/', methods=['GET'])
def redirect_to_register():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():

    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, first_name, last_name, email)

        db.session.commit()
        session['username'] = new_user.username

        flash(f'Success! Registered user {username}.')
        return redirect('/secret')
    
    else:
        return render_template('users/register.html', form=form)
    

@app.route('/secret', methods=['GET'])
def show_secret_page():

    if 'username' in session:
        return render_template('general/secret.html')
    
    else:
        flash('Sorry, you must login to view secret page.')
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def handle_login():

    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # returns user or false
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
            return render_template('users/login.html', form=form)
        
    return render_template('users/login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():

    session.pop('username')
    flash("You've been logged out.")
    return redirect('/login')


@app.route('/users/<username>', methods=['GET'])
def show_user(username):

    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)
    form = DeleteForm()

    return render_template('users/details.html', user=user, form=form)

    
@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):

    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    
    flash(f'User {username} successfully deleted.')
    return redirect('/login')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):

    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm()
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f'/users/{username}')
    
    return render_template('feedback/add.html', form=form)


# ______________________ Feedback Routes ______________________


@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def edit_feedback(feedback_id):

    feedback = Feedback.query.get(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{feedback.username}')
    
    return render_template('/feedback/edit.html', form=form, feedback=feedback)


@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):

    feedback = Feedback.query.get(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

        flash(f'Feedback successfully deleted.')

    return redirect(f'/users/{feedback.username}')



