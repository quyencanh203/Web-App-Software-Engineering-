from db_config import *
from User import *
from Utils import *


class Tutor(User, Utils):
    @staticmethod
    def Class():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM classes WHERE status = 'Chưa có gia sư'")
        new_classes = cursor.fetchall()
        cursor.close()
        return render_template('tutor/class.html', new_classes=new_classes)

    @staticmethod
    def detail(class_id):
        # Kết nối đến cơ sở dữ liệu
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM classes WHERE class_id = %s", (class_id,))

        # Thực hiện truy vấn SQL để lấy thông tin lớp học từ cơ sở dữ liệu

        class_info = cursor.fetchone()
        cursor.close()
        # Trả về trang detail.html với thông tin lớp học được truy vấn từ cơ sở dữ liệu
        return render_template('tutor/detail.html', class_info=class_info)

    @staticmethod
    def register_class(class_id):
        # Kiểm tra xem người dùng đã đăng nhập chưa
        if not session.get('loggedin'):
            flash('Bạn phải đăng nhập để đăng kí nhận lớp.', 'danger')
            return redirect(url_for('login'))


        # Lấy user_id từ session

    
    
        user_id = session.get('user_id')

    # Thực hiện truy vấn SQL để lấy tutor_id và giá tiền một buổi từ bảng tutor và class
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT tutor_id FROM tutor WHERE user_id = %s", (user_id,))
            tutor = cursor.fetchone()
            if tutor:
                tutor_id = tutor['tutor_id']
            else:
                flash('Bạn phải là gia sư mới có thể đăng kí nhận lớp.', 'danger')
                return redirect(url_for('Class'))

            # Lấy thông tin về giá tiền một buổi từ bảng class
            cursor.execute("SELECT price, session_of_per_week FROM classes WHERE class_id = %s", (class_id,))
            class_info = cursor.fetchone()
            if class_info:
                price_per_session = class_info['price']
                session_of_per_week = class_info['session_of_per_week']
            else:
                flash('Không tìm thấy thông tin lớp học.', 'danger')
                return redirect(url_for('Class'))

            # Tính toán số tiền cần để đăng ký nhận lớp
            required_balance = 0.3 * price_per_session * session_of_per_week * 4

            # Kiểm tra số dư trong tài khoản của gia sư
            cursor.execute("SELECT balance FROM tutor WHERE tutor_id = %s", (tutor_id,))
            tutor_balance = cursor.fetchone()['balance']

            if tutor_balance >= required_balance:
                cursor.execute("INSERT INTO requirement (tutor_id, class_id) VALUES (%s, %s)", (tutor_id, class_id))
                mysql.connection.commit()
                cursor.close()
                flash('Đăng kí nhận lớp thành công!', 'success')
                  # Chuyển hướng về trang nạp thẻ
            else:
                flash('Bạn không đủ tiền để đăng kí lớp học, hãy đến trang nạp thẻ và nạp tiền để nhận lớp')
            # Thêm thông tin vào bảng requirement
            
                

        except Exception as e:
            flash('Đã xảy ra lỗi khi đăng kí nhận lớp. Vui lòng thử lại.', 'danger')
            print(e)  # In ra lỗi để debug

        return redirect(url_for('Class'))

    @staticmethod
    def my_class():
        try:
            # connect database
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
            # get user_id from session
            user_id = session['user_id']
            print(session)
            if not user_id:
                flash('User not logged in')
                return redirect(url_for('home'))
    
            # fetch user data from tutor table
            cur.execute("SELECT * FROM tutor WHERE user_id = %s", (user_id,))
            tutor_db = cur.fetchall()
            print(tutor_db)                
            if not tutor_db:
                flash('tutor data not found')
                cur.close()
                return redirect(url_for('home'))
    
            # get tutor_id from user_db
            tutor_id = tutor_db[0]['tutor_id']
            print('tutor_id -->', tutor_id)
            # fetch class data from classes table
            cur.execute("""
            SELECT classes.*, student.phone_student 
            FROM classes 
            JOIN student ON classes.student_id = student.student_id 
            WHERE classes.tutor_id = %s
        """, (tutor_id,))
            classes_db = cur.fetchall()
            print(classes_db)
            cur.close()

            # connection db
            # connection db
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # get user_id
            user_id = session['user_id']
            print(user_id)
            cur.execute("SELECT * FROM tutor WHERE user_id = %s", (user_id,))
            tutor_db = cur.fetchall()
            tutor_id = tutor_db[0]['tutor_id']
            print(type(tutor_id))
            cur.execute("SELECT * FROM requirement WHERE tutor_id = %s", (tutor_id,))
            requirement_db = cur.fetchall()
            print(type(requirement_db))
            class_ids = []
            requirements = {}  # Dictionary to store status of each class
            for req in requirement_db:
                class_ids.append(req['class_id'])
                requirements[req['class_id']] = req['status']  # Store status of each class

            print(class_ids)
            classes_db2 = []
            for class_id in class_ids:
                cur.execute("SELECT * FROM classes WHERE class_id = %s", (class_id,))
                class_db = cur.fetchone()
                if class_db:
                    class_db['status'] = requirements[class_id]  # Add status to each class
                    classes_db2.append(class_db)
                print(classes_db2)
            cur.close()
            
            return render_template('tutor/my_class.html', classes_db=classes_db, classes_db2=classes_db2)
            
        except Exception as e:
            flash('An error occurred')
            print('An error occurred')
            print(e)
            if 'cur' in locals():
                cur.close()
            return redirect(url_for('home'))            

    def payment():
        if request.method == "POST":
            # Lấy dữ liệu từ form
            amount = request.form["amount"]
            description = request.form["description"]
            proof = request.files["proof"]

            # Kiểm tra xem người dùng đã đăng nhập với vai trò tutor chưa
            if 'user_id' in session:
                user_id = session['user_id']
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT tutor_id, email FROM users JOIN tutor ON users.user_id = tutor.user_id WHERE users.user_id = %s", (user_id,))
                tutor = cur.fetchone()
                
                if tutor:
                    tutor_email = tutor['email']
                    tutor_id = tutor['tutor_id']
                    print(tutor_email)
                    print(tutor_id)
                    print(app.root_path)
                    tutor_payment_dir = os.path.join(app.root_path, 'static/images_user/tutors/' + tutor_email + '/payment')
                    if not os.path.exists(tutor_payment_dir):
                        os.makedirs(tutor_payment_dir)
                    proof_path = os.path.join(tutor_payment_dir, proof.filename)
                    print(proof_path)
                    proof.save(proof_path)

                    # Thêm thông tin thanh toán vào bảng payment
                    cur.execute("INSERT INTO payment (tutor_id, amount_paid, date_payment, img_payment) VALUES (%s, %s, %s, %s)",
                                (tutor_id, amount, datetime.now().date(), '..\static/images_user/tutors/' + tutor_email + '/payment/'+proof.filename))
                    mysql.connection.commit()
                    flash("Thanh toán thành công!")
                    return redirect(url_for("home"))  # Chuyển hướng sau khi thanh toán
                else:
                    flash("Bạn không có quyền thực hiện thanh toán!")
                    return redirect(url_for("home"))  # Chuyển hướng về trang chủ nếu người dùng không phải là tutor

        # Nếu là GET request hoặc nếu có lỗi xảy ra trong POST request, render template payment.html
        return render_template("tutor/payment.html")