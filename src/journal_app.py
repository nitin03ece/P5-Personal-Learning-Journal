from flask import (Flask, render_template, flash, 
                   redirect, url_for, g)
from flask_login import (LoginManager, login_required, login_manager, 
                         login_user, logout_user, current_user)
from flask_bcrypt import check_password_hash
import forms
import models


app = Flask(__name__)
app.secret_key = "dhdjdlijd748590585624734092309uedslgdfid740je.,jdk"
app.config['TESTING'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# This function creates slug for detail page specific to its title
# Also it checks the existing slug and creates a unique one
def slug_generate(form):
    slug = ""
    index = 2
    while True:
        # if the title does not exist in database
        if not models.Journal.select().where(models.Journal.title == 
                form.title.data.strip().lower()).exists():
            slug = str(form.title.data.strip().lower()).split()
            slug = "-".join(slug)
            break
        # if the title exists in database
        if models.Journal.select().where(models.Journal.title == 
                form.title.data.strip().lower()).exists():
            
            # if slug is empty i.e this is the first 
            # time it is entering if block
            if not slug:
                slug = form.title.data.strip().lower()
                slug = slug.split()
                slug.append(str(index))
                slug = "-".join(slug)

            # if slug is not empty enter the else block
            else:
                # if the slug is already in existence
                if models.Journal.select().where(models.Journal.slug == slug):
                    slug = slug.split("-")
                    slug.pop()
                    slug.append(str(index))
                    slug = "-".join(slug)
                # if slug is not in existence
                else:
                    break
                index += 1
    return slug


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    g.user = current_user
    return response


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.peewee.DoesNotExist:
        return None

@app.route('/entries/<username>')
@app.route('/entries')
@login_required
def list(username=None):
    if username:
        posts = (models.Journal
        .select(models.User, models.Journal)
        .join(models.User)
        .where(models.User.username**username)
        .order_by(models.Journal.created_at.desc())
    )
    else:
        posts = models.Journal.select().order_by(models.Journal.created_at.desc())
    return render_template("entries.html", posts=posts)


@app.route('/entries/tag/<tag>')
@login_required
def tag_list(tag):
    posts = (models.Journal
    .select()
    .where(models.Journal.tag == tag)
    .order_by(models.Journal.created_at.desc())
    )
    return render_template("entries.html", posts=posts)


@app.route('/entry/<slug>')
@login_required
def detail(slug):
    post = models.Journal.select().where(models.Journal.slug == slug).get()
    return render_template("detail.html", post=post)


# TO DO: Optimize this editing method
@app.route('/entry/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit(slug):
    post = models.Journal.get(models.Journal.slug == slug)

    form = forms.NewEntryForm()
    form.title.data = post.title
    form.date.data = post.created_at
    form.time_spent.data = post.time_spent
    form.learned.data = post.learned
    form.resourses.data = post.resourses
    form.tag.data = post.tag
    
    if form.validate_on_submit():
        validated_form = forms.NewEntryForm()
        post.title=validated_form.title.data.strip()
        post.created_at=validated_form.date.data
        post.time_spent=validated_form.time_spent.data
        post.learned=validated_form.learned.data.strip()
        post.resourses=validated_form.resourses.data.strip()
        post.tag=validated_form.tag.data.strip()
        post.slug="-".join(str(validated_form.title.data.strip().lower()).split())
        post.save()
        return redirect(url_for("list"))
    return render_template("edit.html", form=form)


@app.route('/entry/delete/<slug>')
@login_required
def delete(slug):
    models.Journal.get(models.Journal.slug == slug).delete_instance()
    return redirect(url_for("list"))


@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    slug = ""
    form = forms.NewEntryForm()
    if form.validate_on_submit():
        slug = slug_generate(form)
        models.Journal.create(
            title=form.title.data.strip(),
            created_at=form.date.data,
            time_spent=form.time_spent.data,
            learned=form.learned.data.strip(),
            resourses=form.resourses.data.strip(),
            tag=form.tag.data.strip(),
            slug=slug,
            user=models.User.select().where(models.User.id == current_user.id).get()
        )
        flash("New Journal Entry Posted!", "success")
        return redirect(url_for("list"))
    return render_template("new_entry.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = models.User.get(models.User.username == form.username.data)
        if user != None:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Incorrect username or password", "error")
        else:
            flash("Incorrect username or password", "error")
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template("register.html", form=form)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    models.initialize()
    app.run(debug=True, port=5000, host="127.0.0.1")
