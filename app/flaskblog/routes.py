import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, EvaluateForm, StudentSearchForm, RotationForm, UpdateAccountForm #StudentRegForm
from flaskblog.models import User, Post, Comp, Student, Competancy_rec, User2, Activity
from flask_login import login_user, current_user, logout_user, login_required
import flask_excel as excel
import json


posts = [

    {
        'author': 'Admin',
        'title': 'Marking Dates',
        'content': 'Marking for Clinicial Pathology begins on Wednesday 1st May, 2019!',
        'date_posted': 'April 18, 2019'
    },
    {
        'author': 'Admin',
        'title': 'Registration Of Students',
        'content': 'Student Registration begins on Monday 1st July, 2019.',
        'date_posted': 'April 18, 2019'
    },

]
@app.before_first_request
def setup():
    db.Model.metadata.create_all(bind=db.engine)

@app.route("/")

@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about", methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        def comp_init_func(row):
            c = Comp(row['Code'],row['Rotation Name'], row['Description'])
            return c
            
        request.save_to_database(
            field_name ='file', session=db.session,
            table=Comp,
            initializer=comp_init_func)
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User2(username=form.username.data, email=form.email.data, level=form.level.data, rotation=form.rotation.data, password=hashed_password)
        activity = Activity(activityType='AC', actionID=user.id, clincianID=current_user.id)
        db.session.add(user)
        db.session.add(activity)
        db.session.commit()
        flash('The account has been created! The Clinician should now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User2.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, Please check email and Password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='profilepics/'+current_user.image_file)
    return render_template('account.html', title='Account.html', image_file=image_file)

@app.route("/usersreg")
@login_required
def competancy():
    records= User2.query.all()
    return render_template('usersreg.html', title='usersreg.html', User2=records)

@app.route("/rotations", methods=['GET'])
@login_required
def rotations():
    records = Comp.query.all()
    # resp = []
    # for rec in records:
    #     r = rec.__dict__
    #     r.pop('_sa_instance_state')
    #     resp.append(r)
    # print(resp)
    # return json.dumps(resp)
    return render_template('rotations.html', title='Rotations.html', Comp=records)

@app.route("/evaluate", methods=['GET', 'POST'])
@login_required
def evaluate():
    # form = StudentSearchForm(request.flaskform)
    # if request.method == 'POST':
    # name=request.form['StudentId']
    # return redirect(url_for('home'))
    return render_template('evaluate.html', title='Evaluate.html')

@app.route("/student/<id>", methods=['GET'])
@login_required
def getstudent(id):
    s_rec= Student.query.filter_by(id = id).first()
    if s_rec == None:
        return jsonify({"error":"No Student Exists"})
    s_rec = s_rec.__dict__
    s_rec.pop('_sa_instance_state')
    return jsonify(s_rec)

@app.route("/students", methods=['GET', 'POST'])
@login_required
def students():
    #form = StudentSearchForm()
    if request.method == 'POST':
        def stu_init_func(row):
            s = Student(row['id'],row['Student Name'], row['Date Enrolled'], row['Email'])
            return s
            
        request.save_to_database(
            field_name ='file', session=db.session,
            table=Student,
            initializer=stu_init_func)
    # def export_records():
    #     return excel.make_response_from_array([[1, 2], [3, 4]], "csv", file_name="export_data")
    # def download_file():
    #     return excel.make_response_from_array([[1, 2], [3, 4]], "csv")
    # def handson_table():
    #     return excel.make_response_from_tables(db.session, [Student], 'students.html')

    # export_records()
    # download_file()
    # handson_table()
    records = Student.query.all()
    comp_tbl = Comp.query.all()
    for r in records:
        # test=r.id
        for c in comp_tbl:
            d = Competancy_rec(mark=0, comp_id=c.id, clinician_id='1', student_id=r.id,)
            db.session.add(d)
    db.session.commit()
    return render_template('students.html', title='Students.html', Student=records)

@app.route("/reports")
@login_required
def reports():
    return render_template('reports.html', title='Reports.html')

@app.route("/reminders")
@login_required
def reminders():
    return render_template('reminders.html', title='Reminders.html')

@app.route("/studentRecord")
@login_required
def studentRecord():
    return render_template('studentRecord.html', title='studentRecord.html')

@app.route("/test")
#@login_required
def test():
    return app.send_static_file('test.html')

@app.route("/searchstudent/<s_id>")
def searchstudent(s_id):
    record = Student.query.filter_by(id=s_id).first().__dict__
    record.pop('_sa_instance_state')
    return json.dumps(record)

@app.route("/comp_rec/<student_id>", methods=['GET'])
@login_required
def comp_rec(student_id):
    records= Competancy_rec.query.filter_by(student_id=student_id).all()
    # records = db.session.query(Competancy_rec)
    # .join(Comp, Comp.id==Competancy_rec.comp_id)
    # .all()
    print (records)
    output = {"data":[]}
    for r in records:
        print (r)
        r2 = r.__dict__
        r2.pop('_sa_instance_state')
        output["data"].append(r2)
    return jsonify(output)

@app.route("/update_rec/<comp_rec>/<mark>")
@login_required
def update_rec(comp_rec, mark):
    try:
        if mark == "false":
            mark = 0
        else:
            mark = 1
        record= Competancy_rec.query.filter_by(id=int(comp_rec)).first()
        record.mark = int(mark)
        db.session.commit()
        return jsonify({"success":"record updated"})
    except Exception as e:
        print(e)
        return jsonify({"error":"Error has occured"})

@app.route("/activity", methods=['GET'])
@login_required
def activity():
    records = Activity.query.all()
    return render_template('activity.html', title='Activity.html', Activity=records)

@app.route("/export", methods=['POST', 'GET'])
@login_required
def export():
    if request.method == 'POST':
        def doexport():
            return excel.make_response_from_tables(db.session, [Category, Post], "xls")
        
    return render_template('export.html', title='Export.html')

@app.route("/handson_view", methods=['GET'])
def handson_table():
    return excel.make_response_from_tables(db.session, [Competancy_rec], 'handsontable.html')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext 
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)

    output_size =(125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/accmgmt", methods=['GET', 'POST'])
@login_required
def accmgmt():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file =save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('accmgmt'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profilepics/'+current_user.image_file)
    return render_template('accmgmt.html', title='Account Management', image_file=image_file, form=form)
