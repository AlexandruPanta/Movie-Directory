from flask import Flask,  render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt 
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import BadSignature
from mysql.connector import IntegrityError
from decouple import config
import requests
import mysql.connector 

DB_HOST = config('DB_HOST')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_NAME = config('DB_NAME')
MAIL_PASSWORD = config('MAIL_PASSWORD')
SECRET_KEY = config('SECRET_KEY')
API_KEY = config('API_KEY')
app = Flask(__name__)

bcrypt = Bcrypt(app)

app.secret_key = SECRET_KEY

reset_token_serializer = Serializer(app.secret_key)  


mydb = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = mydb.cursor()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'moviedirectory12@gmail.com'
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    user_logged_in = session.get('user_logged_in', False)
    username = session.get('username', None)
    error_message = None
    api_key = "1532401c"
    movies_to_display = [
        {
            'title': 'Matrix',
            'year': '1999'
        },
        {
            'title': 'Inception',
            'year': '2010'
        },
        {
            'title': 'Avatar',
            'year': '2009'

        },
        {
            'title': 'Interstellar',
            'year': '2014'

        },
        {
            'title': 'Forrest Gump ',
            'year': '1994'

        },
    ]
    movie_data_list = []
    for movie_info in movies_to_display:
        movie_name = movie_info['title']
        year_movie = movie_info['year']
        if year_movie.__len__() <= 0:
            api_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
        else:
            api_url = f"http://www.omdbapi.com/?t={movie_name}&y={year_movie}&apikey={api_key}"
        response = requests.get(api_url)
        if response.status_code == 200:
            my_response = response.json()
            if my_response.get('Response') == 'True':
                ratings = my_response['Ratings'][0]
                all_ratings = ratings['Value']
                movie_id = my_response['imdbID']
                movie_data = {
                    'title': my_response['Title'],
                    'poster': my_response['Poster'],
                    'year': my_response['Year'],
                    'runtime': my_response['Runtime'],
                    'rated': all_ratings,
                    'genre': " ".join(my_response['Genre'].split(",")),
                    'plot': my_response['Plot'],
                    'actors': my_response['Actors'],
                    'rated_class': my_response['Rated']
                }
                movie_data_list.append(movie_data)
    if request.method == 'POST':
        api_key = "ca53cc6b"
        movie_name = request.form['movie_name']
        year_movie = request.form['year_movie']
        if year_movie.__len__() <= 0:
            api_url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
        else:
            api_url = f"http://www.omdbapi.com/?t={movie_name}&y={year_movie}&apikey={api_key}"
        response = requests.get(api_url)
        if response.status_code == 200:
            my_response = response.json()
            if my_response.get('Response') == 'True':
                ratings = my_response['Ratings'][0]
                all_ratings = ratings['Value']
                movie_id = my_response['imdbID']
                movie_data = {
                    'title': my_response['Title'],
                    'poster': my_response['Poster'],
                    'year': my_response['Year'],
                    'runtime': my_response['Runtime'],
                    'rated': all_ratings,
                    'genre': " ".join(my_response['Genre'].split(",")),
                    'plot': my_response['Plot'],
                    'actors': my_response['Actors'],
                    'rated_class': my_response['Rated']
                }
                mycursor = mydb.cursor()
                mycursor.execute("SELECT * FROM comments WHERE movie_id = %s ORDER BY created_at DESC", (movie_id,))
                comments = mycursor.fetchall()
                return render_template('result_movie.html',comments=comments, movie_id=movie_id, user_logged_in=user_logged_in, username=username, **movie_data)
            else:
                error_message = "Movie not found"
        else:
             error_message = f"Request failed with status code: {response.status_code}"
    return render_template('index.html', user_logged_in=user_logged_in, username=username, error_message=error_message,movie_data_list=movie_data_list)

@app.route('/login_site.html',methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT password, IdUser FROM user WHERE name = %s",(username,))
        stored_data = mycursor.fetchone()
        mycursor.close()
        if stored_data:
            stored_password_hash = stored_data[0]
            user_id = stored_data[1]
            if bcrypt.check_password_hash(stored_password_hash, password):
                session['user_logged_in'] = True
                session['username'] = username
                session['user_id']  = user_id
                return redirect(url_for("index"))
            else:
                error_message = "Invalid username or password !"
        else:
            error_message = "Invalid username or password !"
    return render_template('login_site.html', error_message=error_message)

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    error_message = None
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        if not username or not password or not email:
            error_message = "All fields are required!"
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            mycursor = mydb.cursor()
            try:
                mycursor.execute("INSERT INTO user (name,password,email) VALUES (%s,%s,%s)", (username, hashed_password, email))
                mydb.commit()
                return redirect(url_for('login'))
            except IntegrityError as error:
                if error.errno == 1062:
                    error_message = "Username or email already exists."
                else:
                    error_message = "An error occurred while registering."
            finally:
                mycursor.close()
    return render_template('register.html', error_message=error_message)

@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

def generate_reset_token(username):
    return reset_token_serializer.dumps({'username': username}, salt= 'reset-password')
    
@app.route('/forgotpas.html',methods=['GET', 'POST'])
def forgotpas():
    mesage = ""
    error_message = None
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        if not username or not email:
            error_message = "All fields are required !"
        else:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT email FROM user WHERE name = %s",(username,))
            email_stored = mycursor.fetchone()
            if email_stored and email_stored[0] == email:
                token = generate_reset_token(username)  
                reset_link = url_for('reset_password_page', token=token, _external=True)
                msg = Message('Reset Your Password Movie Directory', sender='movie.directory1@gmail.com', recipients=[email])
                msg.body = f"To reset your password, please click here: {reset_link}"
                mail.send(msg)
                mesage = "Message sent!"
            else:
                error_message = "Invalid Username or Email !"
    return render_template('forgotpas.html',error_message=error_message, mesage=mesage)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_page(token):
    error_message = None
    mycursor = None
    if request.method == 'POST':
        new_password = request.form['new_password']
        try:
            token_data = reset_token_serializer.loads(token, salt='reset-password', max_age=3600) 
            username = token_data.get('username')
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE user SET password = %s WHERE name = %s", (hashed_password, username))
            mydb.commit()
            return redirect(url_for('login'))
        except BadSignature:
            error_message = "Invalid or expired token."
        finally:
            if mycursor is not None:
                mycursor.close() 
    return render_template('reset_password.html', token=token, error_message=error_message)

@app.route('/add_comment/<string:movie_id>', methods=['POST'])
def add_comment(movie_id):
    message = None
    if 'user_logged_in' in session:
        username = session['username']
        comment_text = request.form['comment']
        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO comments (movie_id, username, comment) VALUES (%s, %s, %s)", (movie_id, username, comment_text))
        mydb.commit()
    else:
        message = "You have to be logged in to add a comment"
        return redirect(url_for('comment', message=message))
    return redirect(url_for('comment', movie_id=movie_id))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    admin_id = session.get('user_id', None)
    if 'user_logged_in' in session and admin_id == 2:
        mycursor = mydb.cursor()
        mycursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        mydb.commit()
    return redirect(request.referrer)

@app.route('/comment_page/<movie_id>', methods=['GET', 'POST'])
def comment(movie_id):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM comments WHERE movie_id = %s ORDER BY created_at DESC", (movie_id,))
    comments = mycursor.fetchall()
    user_logged_in = session.get('user_logged_in', False)
    username = session.get('username', None)
    user_id = session.get('user_id',None)
    if user_id == 2:
        admin_id = session.get('user_id', None)
        return render_template('comment.html', comments=comments, movie_id=movie_id, user_logged_in=user_logged_in, username=username, admin_id=admin_id)
    else:
        return render_template('comment.html', comments=comments, movie_id=movie_id, user_logged_in=user_logged_in, username=username)

@app.route('/register.html')
def register_page():
    return render_template('register.html')

@app.route('/forgotpas.html')
def forgotpas_page():
    return render_template('forgotpas.html')

@app.route('/index.html')
def redirect_to_index():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(port=8000)
