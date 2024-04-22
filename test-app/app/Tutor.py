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
        cursor.execute("SELECT * FROM classes WHERE class_id = %s", (class_id,)) 
        
    
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

        # Thực hiện truy vấn SQL để lấy tutor_id từ bảng tutor
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT tutor_id FROM tutor WHERE user_id = %s", (user_id,))
            tutor = cursor.fetchone()
            if tutor:
                tutor_id = tutor['tutor_id']
            else:
                flash('Bạn phải là gia sư mới có thể đăng kí nhận lớp.', 'danger')
                return redirect(url_for('Class'))
            
            # Thêm thông tin vào bảng requirement
            cursor.execute("INSERT INTO requirement (tutor_id, class_id) VALUES (%s, %s)", (tutor_id, class_id))
            mysql.connection.commit()
            cursor.close()
            flash('Đăng kí nhận lớp thành công!', 'success')
        except Exception as e:
            flash('Đã xảy ra lỗi khi đăng kí nhận lớp. Vui lòng thử lại.', 'danger')
            print(e)  # In ra lỗi để debug
    
        return redirect(url_for('Class'))