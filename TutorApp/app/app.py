from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
from datetime import datetime
import MySQLdb.cursors

app = Flask(__name__)

# Required
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_PORT"] = 3306 
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "db_tutor"

app.config["SECRET_KEY"] = 'secret_key'

mysql = MySQL(app)

@app.route('/home')
def home():
    # check loggedin 
    if not session.get('loggedin'):
        return redirect(url_for('login'))
    return render_template('common/index.html')

# class 
@app.route('/Class')
def Class():
   # Truy vấn cơ sở dữ liệu để lấy danh sách các lớp học mới
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM classes WHERE status = 'Chưa có gia sư'")  # Lấy danh sách các lớp học chưa có gia sư
    new_classes = cursor.fetchall()
    cursor.close()

    # Hiển thị thông tin của lớp học mới lên trang của gia sư
    return render_template('tutor/class.html', new_classes=new_classes)

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
           session['user_id'] = user[0]  # Truy cập id thông qua chỉ số
           session['name'] = user[1]  # Truy cập tên thông qua chỉ số
           session['role'] = user[5]
           flash('Logged in successfully!', category = 'success')
           return redirect(url_for('home'))
        else:
            flash('Incorrect email or password', category = 'danger')
            return render_template('auth/login.html')

    return render_template('auth/login.html')

@app.route('/registerS', methods=['GET', 'POST'])
def registerS():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        sex = request.form['sex']
        role = request.form['role']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        # Create cursor
        cur = mysql.connection.cursor()

        try:
            # Execute SQL query to insert user data
            cur.execute("INSERT INTO users (name, email, password, sex, role) VALUES (%s, %s, %s, %s, %s)", (name, email, hashed_password, sex, role))
            
            # Get the ID of the inserted user
            user_id = cur.lastrowid

            # Execute SQL query to insert student data
            cur.execute("INSERT INTO student (user_id) VALUES (%s)", (user_id,))
            
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
            return redirect(url_for('registerS'))

    return render_template('auth/registerS.html')


@app.route('/logout')
def logout():
    session['loggedin'] = False 
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    flash('Logged out successfully!', category = 'success')
    return redirect(url_for('login'))

@app.route('/registerT', methods=['GET', 'POST'])
def registerT():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        sex = request.form['sex']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        phone_tutor = request.form['phone_tutor']
        date_of_birth_tutor = request.form['date_of_birth_tutor']
        education = request.form['education']

        # Create cursor
        cur = mysql.connection.cursor()

        try:
            # Execute SQL query to insert user data
            cur.execute("INSERT INTO users (name, email, password, sex, role) VALUES (%s, %s, %s, %s, 'tutor')", (name, email, hashed_password, sex))
            
            # Get the ID of the inserted user
            user_id = cur.lastrowid

            # Execute SQL query to insert tutor data
            cur.execute("INSERT INTO tutor (user_id, phone_tutor, date_of_birth_tutor, education) VALUES (%s, %s, %s, %s)", (user_id, phone_tutor, date_of_birth_tutor, education))
            
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
            return redirect(url_for('registerT'))

    return render_template('auth/registerT.html')

# profile 
@app.route('/home/profile')
def profile():
    # Kết nối đến cơ sở dữ liệu
    cur = mysql.connection.cursor()
    
    user_id = session['user_id']
    
    # Truy vấn dữ liệu từ bảng người dùng
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if session['role'] == 'tutor':
        # Truy vấn dữ liệu từ bảng tutor
        cur.execute("SELECT * FROM tutor WHERE user_id = %s", (user_id,))
        tutor = cur.fetchone()
    
        # Đóng kết nối
        cur.close()
        
        # Trả về trang profile và truyền dữ liệu người dùng
        return render_template('common/profile.html', user=user, tutor = tutor)
    elif session['role'] == 'student':
        # Truy vấn dữ liệu từ bảng tutor
        cur.execute("SELECT * FROM student WHERE user_id = %s", (user_id,))
        student = cur.fetchone()
    
        # Đóng kết nối
        cur.close()
        print('student infor : ')
        print(student)
        print('user infor')
        print(user)

        # Trả về trang profile và truyền dữ liệu người dùng
        return render_template('common/profile.html', user=user, student = student)


# post website
@app.route('/home/post',methods=['GET', 'POST'])
def post():
    # ket no database
    cur = mysql.connection.cursor()

    # lay user_id nguoi dang dang nhap 
    user_id = session['user_id']
    
    # Truy vấn dữ liệu từ bảng người dùng
    cur.execute("SELECT * FROM student WHERE user_id = %s", (user_id,))

    # luu thong tin vao user 
    student = cur.fetchone()

    cur.close()

    if request.method == 'POST':
        student_id = student[0]
        class_student = request.form['class_student']
        subject = request.form['subject']
        address = request.form['address']
        booking_date = datetime.now()
        price = request.form['price']
        description = request.form['description']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO classes (student_id, class_student, subject, address, status, description, booking_date, price) VALUES (%s, %s, %s ,%s, %s, %s, %s, %s)', (student_id, class_student, subject, address, 'Chưa có gia sư', description,booking_date, price))
        mysql.connection.commit()
        cursor.close()
    return render_template('student/post.html')
# dang code 
@app.route('/home/profile/update_profile', methods=['GET', 'POST'])
def update_profile():
    cur = mysql.connection.cursor()
    user_id = session['user_id']

    if request.method == 'POST':
        # Nhận thông tin từ form
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        date_of_birth = request.form['date_of_birth']

        # Cập nhật thông tin người dùng
        cur.execute("""
            UPDATE users 
            SET name = %s, email = %s
            WHERE user_id = %s
        """, (name, email,  user_id))
        
        if session['role'] == 'student':
            cur.execute("""
                UPDATE student
                SET phone_student = %s, date_of_birth_student = %s
                WHERE  user_id = %s
            """, (phone, date_of_birth,  user_id))

        if session['role'] == 'tutor':
            cur.execute("""
                UPDATE tutor
                SET phone_tutor = %s, date_of_birth_tutor = %s
                WHERE  user_id = %s
            """, (phone, date_of_birth,  user_id))
        
        # Lưu thay đổi
        mysql.connection.commit()

        # Đóng kết nối
        cur.close()

        # Chuyển hướng về trang profile sau khi cập nhật
        return redirect(url_for('profile'))

    elif request.method == 'GET':
        # Truy vấn thông tin người dùng hiện tại
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()

        # Đóng kết nối
        cur.close()

        return render_template('common/update_profile.html', user=user)

if __name__ == '__main__':
    app.run('0.0.0.0', '5000', debug=True)

