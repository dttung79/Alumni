from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import hashlib
import os
from gen_invite import create_invitation
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

@app.route('/')
def index():
    return build_page('index.html')

@app.route('/register')
def register():
    return build_page('register.html')

@app.route('/submit_alumni', methods=['POST'])
def submit_alumni():
    # check if file is too large
    if request.content_length > app.config['MAX_CONTENT_LENGTH']:
        return render_template('error.html', error='File is too large. Maximum file size is 5MB.')
    # get form data
    name, email, phone, alumni, major, facebook = get_form_data()
    # check if photo part is in the request
    if 'photo' not in request.files:
        return render_template('error.html', error='No photo part in the request.')
    photo_file = request.files['photo']
    # check if photo part is empty
    if photo_file.filename == '':
        return render_template('error.html', error='No selected file.')
    
    if photo_file:
        filename = save_photo(photo_file, name, email)
    try:
        invitation_file = create_invitation(filename, name)
        save_data(name, email, alumni, major, facebook, filename)
        email_data(name, email, phone, alumni, major, facebook)
        return gen_invitation(invitation_file)
    except Exception as e:
        return render_template('error.html', error='No face detected in the portrait image.')

@app.route('/all')
def all():
    alumni_folder = 'static/alumni'
    student_info = []

    # Iterate over each file in the alumni folder
    for filename in os.listdir(alumni_folder):
        if filename == 'keep':
            continue
        file_path = os.path.join(alumni_folder, filename)
        # Check if the file is a file (not a folder) and skip .file files
        if os.path.isfile(file_path) and not filename.startswith('.'):
            with open(file_path, 'r') as file:
                # Read the content of the file and append it to the student_info list
                content = file.read().splitlines()
                student_info.append(content)

    return jsonify(student_info)
@app.route('/clear')
def clear():
    # delete all files in the alumni folder
    delete_files('static/alumni')
    delete_files('static/uploads')
    delete_files('static/invite')
    return 'All files are deleted'

@app.route('/clear/<filename>')
def clear_file(filename):
    # delete the file with the given filename in the alumni folder
    os.remove(f'static/alumni/{filename}.txt')
    # delete the file with the given filename no matter what extension in the uploads folder
    for f in os.listdir('static/uploads'):
        if f.startswith(filename):
            os.remove(f'static/uploads/{f}')
    # delete the file with the given filename no matter what extension in the invite folder
    for f in os.listdir('static/invite'):
        if f.startswith(filename):
            os.remove(f'static/invite/{f}')
    return 'File is deleted'
@app.route('/static/alumni/list')
def static_alumni():
    # return all files in the alumni folder
    files = []
    for f in os.listdir('static/alumni'):
        if f == 'keep':
            continue
        files.append(f)
    return jsonify(files)

@app.route('/static/uploads/list')
def static_uploads():
    # return all files in the uploads folder
    files = []
    for f in os.listdir('static/uploads'):
        files.append(f)
    return jsonify(files)

@app.route('/static/invite/list')
def delete_files(folder):
    for filename in os.listdir(folder):
        if filename == 'keep':
            continue
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) and not filename.startswith('.'):
            os.remove(file_path)

def gen_invitation(filename):
    # build a html page with the invitation
    content = render_template('invite.html', filename=filename)
    return content

def email_data(name, email, phone, alumni, major, facebook):
    sender_email = "alumnigreenwichhn@gmail.com"
    receiver_email = "longnn22@fe.edu.vn"
    password = 'ylsx tldk cltf xsps'
    #password = "zcbm135&("

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Alumni Data for {name}"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"""
    Name: {name}
    Email: {email}
    Phone: {phone}
    Alumni: {alumni}
    Major: {major}
    Facebook: {facebook}
    """

    html = f"""
    <html>
        <body>
            <h2>Alumni Data</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Alumni:</strong> {alumni}</p>
            <p><strong>Major:</strong> {major}</p>
            <p><strong>Facebook:</strong> {facebook}</p>
        </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    
def save_data(name, email, alumni, major, facebook, filename):
    filename_noext = filename.split('/')[-1].split('.')[0]
    with open(f'static/alumni/{filename_noext}.txt', 'w') as f:
        f.write(name + '\n')
        f.write(email + '\n')
        f.write(alumni + '\n')
        f.write(major + '\n')
        f.write(facebook + '\n')
        f.write(filename.split('/')[-1])

def save_photo(photo_file, name, email):
    ext = photo_file.filename.split('.')[-1]
    # check extension
    if ext.lower() not in ['jpg', 'jpeg', 'png', 'bmp', '.svg']:
        return render_template('error.html', error='Only jpg, jpeg, png, bmp and svg files are allowed.')
    filename = secure_filename(photo_file.filename)
    filename += name + email
    filename = hashlib.md5(filename.encode()).hexdigest()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.' + ext)
    photo_file.save(full_filename)
    return full_filename

def get_form_data():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    alumni = request.form['alumni']
    major = request.form['major']
    facebook = request.form['facebook']
    
    return name, email, phone, alumni, major, facebook

def build_page(filename):
    content = render_template(filename)
    return content

####### main function #######
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')