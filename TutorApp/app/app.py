from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
from datetime import datetime

app = Flask(__name__)

# Required
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_PORT"] = 3306 
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "quan342004q"
app.config["MYSQL_DB"] = "mydata2"
app.config["SECRET_KEY"] = 'secret_key'

mysql = MySQL(app)

@app.route('/home')
def home():
    # check loggedin 
    if not session.get('loggedin'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    session['loggedin'] = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        # creating a connection cursor 
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password, user[3].encode('utf-8')):  # Truy cập mật khẩu thông qua chỉ số

           # set session variable
           session['loggedin'] = True
           session['id'] = user[0]  # Truy cập id thông qua chỉ số
           session['name'] = user[1]  # Truy cập tên thông qua chỉ số
           flash('Logged in successfully!', category = 'success')
           return redirect(url_for('home'))
        else:
            flash('Incorrect email or password', category = 'danger')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        # Create cursor
        cur = mysql.connection.cursor()

        try:
            # Execute SQL query
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            
            # Commit the transaction
            mysql.connection.commit()

            # Close the cursor
            cur.close()

            flash('Registered successfully! You can now login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash('An error occurred while registering. Please try again.', 'danger')
            print(e)
            cur.close()
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session['loggedin'] = False 
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    flash('Logged out successfully!', category = 'success')
    return redirect(url_for('login'))

@app.route('/home/registerTutor')
def registerTutor():
    return render_template('registerTutor.html')

@app.route('/home/profile')
def profile():
    return render_template('profile.html')

# post website
@app.route('/home/post',methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        subject = request.form['subject']
        class_student = request.form['class_student']
        booking_date = datetime.now()
        price = request.form['price']
        describe_request = request.form['describe_request']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO booking (subject, class_student, booking_date, status_booking, price, describe_request) VALUES (%s, %s, %s, %s, %s, %s)', (subject, class_student, booking_date, 'Pending', price, describe_request))
        mysql.connection.commit()
        cursor.close()
    return render_template('post.html')

if __name__ == '__main__':
    app.run('0.0.0.0', '5000', debug=True)
