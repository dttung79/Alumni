from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import hashlib
import os
from gen_invite import create_invitation

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
        return 'File is too large', 413
    # get form data
    name, email, alumni, major, facebook = get_form_data()
    # check if photo part is in the request
    if 'photo' not in request.files:
        return 'No photo part', 400
    photo_file = request.files['photo']
    # check if photo part is empty
    if photo_file.filename == '':
        return 'No selected file', 400
    
    if photo_file:
        filename = save_photo(photo_file, name, email)

    save_data(name, email, alumni, major, facebook, filename)
    try:
        invitation_file = create_invitation(filename, name)
        return gen_invitation(invitation_file)
    except Exception as e:
        return render_template('error.html', error='No face detected in the portrait image.')

@app.route('/all')
def all():
    alumni_folder = 'static/alumni'
    student_info = []

    # Iterate over each file in the alumni folder
    for filename in os.listdir(alumni_folder):
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

def delete_files(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
def gen_invitation(filename):
    # build a html page with the invitation
    content = render_template('invite.html', filename=filename)
    return content

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
    filename = secure_filename(photo_file.filename)
    filename += name + email
    filename = hashlib.md5(filename.encode()).hexdigest()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.' + ext)
    photo_file.save(full_filename)
    return full_filename

def get_form_data():
    name = request.form['name']
    email = request.form['email']
    alumni = request.form['alumni']
    major = request.form['major']
    facebook = request.form['facebook']
    
    return name, email, alumni, major, facebook

def build_page(filename):
    content = render_template(filename)
    return content

####### main function #######
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')