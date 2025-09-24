import sqlite3
import hashlib
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g

# ------------------- 配置 -------------------
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

DATA_DIR = 'data'
DATABASE_FILE = os.path.join(DATA_DIR, 'database.db')

SECRET_KEY = 'your_very_secret_key_change_it_for_security'

# 多语言配置
SUPPORTED_LANGS = {'en', 'ar'}
DEFAULT_LANG = 'en'
TRANSLATIONS = {
    'en': {
        # General
        'app_title': 'Queue System',
        'switch_to_en': 'English',
        'switch_to_ar': 'العربية',
        'unauthorized': 'Unauthorized',
        'request_failed': 'Request failed. Please try again.',
        'op_failed_try_again': 'Operation failed. Please try again.',

        # Customer Page
        'welcome': 'Welcome',
        'smart_queue': 'Get your ticket for our smart queue system.',
        'current_queue': 'Current Queue Status',
        'now_calling': 'Now Calling',
        'waiting_tables': 'Waiting',
        'my_queue_info': 'My Queue Information',
        'your_number': 'Your Number:',
        'status': 'Status',
        'clear_my_number': 'Cancel My Ticket',
        'enter_party_size': 'How many people in your party?',
        'party_size_placeholder': 'e.g., 4',
        'take_ticket_now': 'Get Ticket',
        'ticket_processed_or_invalid': 'Your ticket has been processed or is invalid.',
        'status_waiting': 'Waiting',
        'status_called': 'Please Proceed',
        'tables_ahead': 'tables ahead of you.',
        'invalid_party_size': 'Please enter a valid party size (a positive number).',
        'taking_ticket': 'Getting ticket...',
        'ticket_success': 'Ticket issued successfully. Your number is {n}.',

        # Admin Page
        'admin_title': 'Admin Dashboard',
        'admin_login': 'Admin Login',
        'admin_welcome': 'Welcome back! Please manage the queue.',
        'username': 'Username',
        'password': 'Password',
        'login': 'Login',
        'login_error': 'Incorrect username or password.',
        'dashboard': 'Dashboard',
        'realtime_manage': 'Manage your customer queue in real-time.',
        'reset_queue': 'Reset Queue',
        'reset_queue_confirm': 'Are you sure you want to delete all tickets and reset the queue?',
        'logout': 'Logout',
        'queue_list': 'Queue List',
        'ticket_no': 'Ticket No.',
        'party_size': 'Size',
        'status_col': 'Status',
        'actions': 'Actions',
        'loading_data': 'Loading data...',
        'load_failed': 'Failed to load queue data.',
        'no_customers': 'No customers in the queue yet.',
        'waiting_count': 'Currently Waiting',
        'tables': 'Tables',
        'scan_to_join': 'Scan to Join Queue',
        'scan_tip': 'Customers can scan this QR code to get a ticket.',
        'qr_alt': 'QR Code to join queue',
        'waiting_badge': 'Waiting',
        'called_badge': 'Called',
        'call': 'Call',
        'seat': 'Seat',
        'requeue': 'Re-Queue',
        'cancel_action': 'Cancel',
        'settings': 'Store Settings',
        'settings_desc': 'Customize public information for your store.',
        'restaurant_name': 'Restaurant Name',
        'welcome_message': 'Welcome Message (Customer Page)',
        'display_header_message': 'Header Message (Display Screen)',
        'save_settings': 'Save Settings',
        'settings_saved': 'Settings saved successfully!',

        # Display Page
        'display_title': 'Queue Display',
        'display_header': 'Welcome',
        'no_calls': 'No numbers are being called currently.',
        'up_next': 'Up Next',
        'none_waiting': 'No one is waiting.',
        'guests': 'guests',
    },
    'ar': {
        # General
        'app_title': 'نظام الطابور',
        'switch_to_en': 'English',
        'switch_to_ar': 'العربية',
        'unauthorized': 'غير مصرح',
        'request_failed': 'فشل الطلب. الرجاء المحاولة مرة أخرى.',
        'op_failed_try_again': 'فشلت العملية. الرجاء المحاولة مرة أخرى.',

        # Customer Page
        'welcome': 'أهلاً وسهلاً',
        'smart_queue': 'احصل على رقمك الآن عبر نظامنا الذكي.',
        'current_queue': 'حالة الطابور الحالية',
        'now_calling': 'جاري النداء',
        'waiting_tables': 'في الانتظار',
        'my_queue_info': 'معلومات رقمي',
        'your_number': 'رقمك هو:',
        'status': 'الحالة',
        'clear_my_number': 'إلغاء رقمي',
        'enter_party_size': 'كم عدد أفراد مجموعتك؟',
        'party_size_placeholder': 'مثال: 4',
        'take_ticket_now': 'احصل على رقم',
        'ticket_processed_or_invalid': 'لقد تمت معالجة رقمك أو أنه غير صالح.',
        'status_waiting': 'في الانتظار',
        'status_called': 'يرجى التوجه للداخل',
        'tables_ahead': 'طاولة أمامك.',
        'invalid_party_size': 'الرجاء إدخال عدد صحيح وصالح للأشخاص.',
        'taking_ticket': 'جاري الحصول على رقم...',
        'ticket_success': 'تم إصدار الرقم بنجاح. رقمك هو {n}.',

        # Admin Page
        'admin_title': 'لوحة تحكم المسؤول',
        'admin_login': 'تسجيل دخول المسؤول',
        'admin_welcome': 'أهلاً بعودتك! يرجى إدارة طابور الانتظار.',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'login': 'تسجيل الدخول',
        'login_error': 'اسم المستخدم أو كلمة المرور غير صحيحة.',
        'dashboard': 'لوحة التحكم',
        'realtime_manage': 'إدارة طابور العملاء في الوقت الفعلي.',
        'reset_queue': 'إعادة تعيين الطابور',
        'reset_queue_confirm': 'هل أنت متأكد أنك تريد حذف جميع الأرقام وإعادة تعيين الطابور؟',
        'logout': 'تسجيل الخروج',
        'queue_list': 'قائمة الانتظار',
        'ticket_no': 'رقم التذكرة',
        'party_size': 'العدد',
        'status_col': 'الحالة',
        'actions': 'الإجراءات',
        'loading_data': 'جاري تحميل البيانات...',
        'load_failed': 'فشل تحميل بيانات الطابور.',
        'no_customers': 'لا يوجد عملاء في الطابور بعد.',
        'waiting_count': 'عدد المنتظرين حالياً',
        'tables': 'طاولات',
        'scan_to_join': 'امسح للانضمام للطابور',
        'scan_tip': 'يمكن للعملاء مسح هذا الرمز للحصول على رقم.',
        'qr_alt': 'رمز QR للانضمام للطابور',
        'waiting_badge': 'منتظر',
        'called_badge': 'تم النداء',
        'call': 'نداء',
        'seat': 'إجلاس',
        'requeue': 'إعادة انتظار',
        'cancel_action': 'إلغاء',
        'settings': 'إعدادات المتجر',
        'settings_desc': 'تخصيص المعلومات العامة لمتجرك.',
        'restaurant_name': 'اسم المطعم',
        'welcome_message': 'رسالة الترحيب (صفحة العملاء)',
        'display_header_message': 'رسالة الرأس (شاشة العرض)',
        'save_settings': 'حفظ الإعدادات',
        'settings_saved': 'تم حفظ الإعدادات بنجاح!',

        # Display Page
        'display_title': 'شاشة العرض',
        'display_header': 'أهلاً وسهلاً',
        'no_calls': 'لا يتم نداء أي أرقام حاليًا.',
        'up_next': 'التالي',
        'none_waiting': 'لا يوجد أحد في الانتظار.',
        'guests': 'أشخاص',
    }
}

# ------------------- 初始化 -------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

PASSWORD_HASH = hashlib.sha256(ADMIN_PASSWORD.encode('utf-8')).hexdigest()


def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number INTEGER NOT NULL,
                party_size INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'waiting',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # 检查并插入默认设置
        default_settings = {
            'restaurant_name': 'My Restaurant',
            'welcome_message': 'Smart Queue System',
            'display_header_message': 'Welcome'
        }
        for key, value in default_settings.items():
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

        conn.commit()
        conn.close()


init_db()


# ------------------- 国际化 & 上下文 -------------------

def _get_lang_from_request():
    q = request.args.get('lang', '').lower().strip()
    if q in SUPPORTED_LANGS: return q
    s = session.get('lang')
    if s in SUPPORTED_LANGS: return s
    return DEFAULT_LANG


@app.before_request
def _set_lang_and_settings():
    lang = _get_lang_from_request()
    session['lang'] = lang
    g.lang = lang
    g.dir = 'rtl' if lang == 'ar' else 'ltr'

    # !!! 关键改动：在这里定义 t 函数并附加到 g 对象 !!!
    def t(key, **kwargs):
        lang = g.lang
        txt = TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))
        return txt.format(**kwargs) if kwargs else txt

    g.t = t

    # 获取并注入设置
    conn = get_db_connection()
    settings_data = conn.execute('SELECT key, value FROM settings').fetchall()
    conn.close()
    g.settings = {row['key']: row['value'] for row in settings_data}


@app.context_processor
def _inject_i18n_and_settings():
    # 这个函数现在只负责向模板注入变量
    def switch_lang_url(lang_code):
        from urllib.parse import urlencode
        args = request.args.to_dict(flat=True)
        args['lang'] = lang_code
        return f"{request.path}?{urlencode(args)}"

    return dict(
        t=getattr(g, 't', lambda key, **kwargs: key),  # 从 g 对象获取 t 函数
        lang=getattr(g, 'lang', DEFAULT_LANG),
        dir=getattr(g, 'dir', 'ltr'),
        switch_lang_url=switch_lang_url,
        settings=getattr(g, 'settings', {})
    )


# ------------------- API 路由 -------------------

@app.route('/api/queue')
def get_queue_status():
    conn = get_db_connection()
    queue_data = conn.execute('SELECT * FROM queue ORDER BY timestamp ASC').fetchall()
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
    data = request.get_json()
    party_size = data.get('party_size')

    if not party_size or not str(party_size).isdigit() or int(party_size) <= 0:
        return jsonify({'success': False, 'message': g.t('invalid_party_size')}), 400

    conn = get_db_connection()
    last_ticket = conn.execute('SELECT MAX(ticket_number) as max_ticket FROM queue').fetchone()
    new_ticket_number = (last_ticket['max_ticket'] or 0) + 1

    conn.execute('INSERT INTO queue (ticket_number, party_size) VALUES (?, ?)',
                 (new_ticket_number, party_size))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'ticket_number': new_ticket_number,
        'message': g.t('ticket_success', n=new_ticket_number)
    })


@app.route('/api/update_status/<int:ticket_id>', methods=['POST'])
def update_ticket_status(ticket_id):
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': g.t('unauthorized')}), 401

    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['called', 'seated', 'cancelled', 'waiting']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400

    conn = get_db_connection()
    conn.execute('UPDATE queue SET status = ? WHERE id = ?', (new_status, ticket_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'Ticket {ticket_id} status updated'})


@app.route('/api/reset_queue', methods=['POST'])
def reset_queue():
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': g.t('unauthorized')}), 401

    conn = get_db_connection()
    conn.execute('DELETE FROM queue')
    conn.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'queue'")
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Queue has been reset'})


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """管理员更新设置"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'message': g.t('unauthorized')}), 401

    data = request.get_json()
    allowed_keys = ['restaurant_name', 'welcome_message', 'display_header_message']

    conn = get_db_connection()
    cursor = conn.cursor()
    for key, value in data.items():
        if key in allowed_keys:
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': g.t('settings_saved')})


# ------------------- 页面路由 -------------------
@app.route('/')
def customer_page():
    return render_template('customer.html')


@app.route('/display')
def display_page():
    return render_template('display.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password_attempt = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if username == ADMIN_USERNAME and hashed_password_attempt == PASSWORD_HASH:
            session['logged_in'] = True
            return redirect(url_for('admin_page'))
        else:
            return render_template('admin.html', error=g.t('login_error'), logged_in=False)

    if 'logged_in' in session:
        host_url = request.host_url
        return render_template('admin.html', logged_in=True, host_url=host_url)

    return render_template('admin.html', logged_in=False)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_page'))


# ------------------- 启动程序 -------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5091)

