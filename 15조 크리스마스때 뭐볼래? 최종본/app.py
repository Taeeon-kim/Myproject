from flask import Flask, render_template, jsonify, request, redirect, url_for
import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from bson.objectid import ObjectId


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta


# 메인 화면 보여주기
@app.route('/', methods=['GET'])
def main():

    all_movies = list(db.movie_list.find({}, {'_id': False}))
    token_receive = request.cookies.get('mytoken')

    # db.movie_list.remove({})
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html', movies=all_movies)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login"))

# 리뷰하기 페이지
@app.route('/review/<title>', methods=['GET'])
def review(title):

    movie_info = db.movie_list.find_one({'movie_name': title}, {'_id': False})
    return render_template('review.html', movie=movie_info)

#
@app.route('/index')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


# @app.route('/api/register')
# def register():
#     return render_template('register.html')


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"id": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    id = request.form['username_give']
    pw = request.form['password_give']

    pw = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    result = db.users.find_one({'id': id, 'pw': pw})

    if result is not None:
        payload = {
            'id': id,
            'exp': datetime.utcnow() + timedelta(seconds=300)  # 로그인 24시간 유지, (10초로 바꿈)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/api/register', methods=['POST'])
def sign_up():
    id= request.form['username_give']
    pw = request.form['password_give']
    pw = hashlib.sha256(
        pw.encode('utf-8')).hexdigest()  # 암호화 하고싶은 변수를쓰고 .encode() 를쓴다. 이때 Utf-8로 변환 시켜주기위해 ''에 넣은것이다
    doc = {
        "id": id,  # 아이디
        "pw": pw,  # 비밀번호
        "profile_name": id,  # 프로필 이름 기본값은 아이디 , 이 부분부터 아래 프로필부분은 사용안함.
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": "",  # 프로필 한 마디
        # "name": name,
        # "p_num": p_num,
        # "address": address,
        # "email": email
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    id = request.form['username_give']
    exists = bool(db.users.find_one({"id": id}))
    return jsonify({'result': 'success', 'exists': exists})




# 리뷰 생성
@app.route('/make_review', methods=['POST'])
def make_review():
    user_id_receive = request.form['user_id_give']
    movie_review_receive = request.form['movie_review_give']

    doc = {
        'user_id': user_id_receive,
        'movie_review': movie_review_receive
    }

    db.moviereview.insert_one(doc)

    return jsonify({'msg': "리뷰를 남기셨습니다"})


# 리뷰 조회
@app.route('/show_review', methods=['GET'])
def show_review():
    movie_reviews = list(db.moviereview.find({}, {'_id': False}))
    return jsonify({'all_reviews': movie_reviews})


# 리뷰 삭제
@app.route('/api/delete', methods=['POST'])
def review_delete():
    movie_review_receive = request.form['movie_review_give']
    db.moviereview.delete_one({'movie_review': movie_review_receive})
    return jsonify({'msg': '삭제되었습니다'})


# 리뷰 수정
@app.route('/api/update', methods=['POST'])
def review_update():
    user_id_receive = request.form['user_id_give']
    movie_review_receive = request.form['movie_review_give']
    db.moviereview.update_one({'user_id': user_id_receive}, {'$set': {'movie_review': movie_review_receive}})
    return jsonify({'msg': '수정되었습니다'})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
