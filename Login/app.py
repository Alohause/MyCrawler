# app.py
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # 用于加密 session 的 key

# 用户数据库（模拟）
USERS = {
    'testuser': '123456'
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        passwd = request.form['password']
        if uname in USERS and USERS[uname] == passwd:
            session['username'] = uname  # 登录成功，记录 session
            return redirect(url_for('userinfo'))
        else:
            return "用户名或密码错误"
    return render_template('login.html')

@app.route('/userinfo')
def userinfo():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('userinfo.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
