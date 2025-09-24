import sqlite3
import hashlib
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

# ------------------- 配置 -------------------
# 重要提示: 为了您的数据安全，请务必修改下面的 ADMIN_PASSWORD 变量的值！
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'
DATABASE_FILE = 'database.db'
SECRET_KEY = 'your_very_secret_key_change_it'  # 用于 session 加密，请修改为随机字符串

# ------------------- 初始化 -------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

# 哈希密码以增加安全性
PASSWORD_HASH = hashlib.sha256(ADMIN_PASSWORD.encode('utf-8')).hexdigest()


def get_db_connection():
    """创建并返回数据库连接"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库，创建表结构"""
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number INTEGER NOT NULL,
                party_size INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'waiting', -- 'waiting', 'called', 'seated', 'cancelled'
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()


# ------------------- 核心 API 路由 -------------------
@app.route('/api/queue')
def get_queue_status():
    """获取当前整个排队列表的状态"""
    conn = get_db_connection()
    queue_data = conn.execute('SELECT * FROM queue ORDER BY ticket_number ASC').fetchall()
    conn.close()

    waiting_list = [dict(row) for row in queue_data if row['status'] == 'waiting']
    called_list = [dict(row) for row in queue_data if row['status'] == 'called']

    return jsonify({
        'waiting': waiting_list,
        'called': called_list,
        'total_waiting': len(waiting_list)
    })


@app.route('/api/take_ticket', methods=['POST'])
def take_ticket():
    """顾客取号"""
    data = request.get_json()
    party_size = data.get('party_size')

    if not party_size or not str(party_size).isdigit() or int(party_size) <= 0:
        return jsonify({'success': False, 'message': '请输入有效的人数'}), 400

    conn = get_db_connection()
    # 查找当前最大的票号
    last_ticket = conn.execute('SELECT MAX(ticket_number) as max_ticket FROM queue').fetchone()
    new_ticket_number = (last_ticket['max_ticket'] or 0) + 1

    conn.execute('INSERT INTO queue (ticket_number, party_size) VALUES (?, ?)',
                 (new_ticket_number, party_size))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'ticket_number': new_ticket_number,
        'message': f'取号成功！您的号码是 {new_ticket_number}。'
    })


@app.route('/api/update_status/<int:ticket_id>', methods=['POST'])
def update_ticket_status(ticket_id):
    """商家更新票号状态 (叫号、入座、取消)"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': '未授权'}), 401

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['called', 'seated', 'cancelled', 'waiting']:
        return jsonify({'success': False, 'message': '无效的状态'}), 400

    conn = get_db_connection()
    conn.execute('UPDATE queue SET status = ? WHERE id = ?', (new_status, ticket_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'号码 {ticket_id} 状态已更新为 {new_status}'})


@app.route('/api/reset_queue', methods=['POST'])
def reset_queue():
    """商家重置清空整个队列"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': '未授权'}), 401

    conn = get_db_connection()
    conn.execute('DELETE FROM queue')
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': '队列已重置'})


# ------------------- 页面路由 -------------------
@app.route('/')
def customer_page():
    """顾客端页面"""
    return render_template('customer.html')


@app.route('/display')
def display_page():
    """大屏展示页面"""
    return render_template('display.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    """商家管理端页面及登录处理"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password_attempt = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if username == ADMIN_USERNAME and hashed_password_attempt == PASSWORD_HASH:
            session['logged_in'] = True
            return redirect(url_for('admin_page'))
        else:
            return render_template('admin.html', error='错误的用户名或密码')

    if 'logged_in' in session:
        # 获取当前服务器地址用于生成二维码
        host_url = request.host_url
        return render_template('admin.html', logged_in=True, host_url=host_url)

    return render_template('admin.html', logged_in=False)


@app.route('/logout')
def logout():
    """登出"""
    session.pop('logged_in', None)
    return redirect(url_for('admin_page'))


# ------------------- 启动程序 -------------------
if __name__ == '__main__':
    init_db()
    print("Flask app is running. Access points:")
    print(f"  - Customer: http://127.0.0.1:5000/")
    print(f"  - Admin:    http://127.0.0.1:5000/admin")
    print(f"  - Display:  http://127.0.0.1:5000/display")
    app.run(debug=True, host='0.0.0.0', port=5000)
