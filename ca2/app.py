from flask import Flask, render_template, request, jsonify, url_for, redirect, session, g
from forms import NameForm
from flask_session import Session
from functools import wraps
from database import get_db, close_db

app=Flask(__name__)

app.config['SECRET_KEY']='secret-key'

app.config['SESSION_PERMANENT']=False
app.config['SESSION_TYPE']='filesystem'
Session(app)

app.config['SECRET_KEY']='secret-key'

@app.teardown_appcontext
def close_db_at_end_of_request (e=None):
    close_db(e)

@app.before_request
def loadloggedinuser():
    g.user=session.get('user', None)

def loginrequired(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index', next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.route("/", methods=['GET', 'POST'])
def index():
    form=NameForm()
    if form.validate_on_submit():
        name=form.name.data
        session.clear()
        session['user']=name
        nextpage=request.args.get('next')
        if not nextpage:
            nextpage=url_for('game')
        return redirect(nextpage)
    return render_template("index.html", form=form)

@app.route("/game")
@loginrequired
def game():
    return render_template("game.html")

@app.route('/scoreboard', methods=['POST'])
def scoreboard():
    score=int(request.form['score'])
    db=get_db()
    if db.execute('''SELECT * FROM scoreboard WHERE name=?;''', (session['user'],)).fetchone() is None:
            db.execute('''INSERT INTO scoreboard(name, score) VALUES(?,?);''', (session['user'],score))
            db.commit()
            print(score)
    else:
        if score> (db.execute('''SELECT score FROM scoreboard WHERE name=?;''', (session['user'],)).fetchone()['score']):
            db.execute('''UPDATE scoreboard SET score=? WHERE name=?;''', (score,session['user']))
            db.commit()
            print(score)
    return 'success'

@app.route("/getscoreboard")
def getscoreboard():
    db=get_db()
    scoreboard=db.execute('''SELECT * FROM scoreboard ORDER BY score DESC;''').fetchall()
    position=[]
    for number in range(1,len(scoreboard)+1):
        position.append(number)
    scoreboard=zip(position,scoreboard)
    return render_template('scoreboard.html', scoreboard=scoreboard)
