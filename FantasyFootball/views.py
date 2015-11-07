"""
Routes and views for the flask application.
"""
import os
from datetime import datetime
from flask import render_template, request, redirect, jsonify, url_for, flash, send_from_directory, Response, make_response
from flask import session as login_session
from flask.ext.seasurf import SeaSurf
from werkzeug import secure_filename
import json
import random
import string
import httplib2
import urllib
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from FantasyFootball import app
from xmlhelper import generate_xml
from FantasyFootball.Model import Base
from FantasyFootball.Model.schema import Team, Player, User

#APPLICATION CONSTANT
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['UPLOAD_FOLDER'] = 'FantasyFootball/static/snaps/'
# Connect to Database
engine = create_engine('sqlite:///fantasyfootball.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine 

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Protecting Fantasyfootball from csrf
csrf = SeaSurf(app)

#Show login page 
@app.route('/login')
def showLogin():
    #store state to avoid cross site frogery
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html',year=datetime.now().year,title='Log in | FantasyFootball',STATE=state)

# Logout and remove session information
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        if login_session['provider'] == 'amazon':
            amazondisconnect()
            del login_session['amazon_id']
        del login_session['username']
        del login_session['email']        
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showTeams'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showTeams'))


@csrf.exempt
@app.route('/amazonconnect', methods=['POST'])
def amazonconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_code  = request.data
    
    # Exchange client toke for long lived server-side token with 
    client_id = json.loads(open('amazon_client_secrets.json', 'r').read())[
        'web']['client_id']
    client_secret = json.loads(
        open('amazon_client_secrets.json', 'r').read())['web']['client_secret']
    url = 'https://api.amazon.com/auth/o2/token'
    
    h = httplib2.Http()
    headers = {'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    body = {'grant_type': 'authorization_code', 'code': access_code,
            'client_id' : client_id, 'client_secret': client_secret}
    
    result = h.request(url, 'POST', headers=headers,body=urllib.urlencode(body))[1]
    
    data=json.loads(result)
    
    # Use token to get user info from API
    access_token=data["access_token"]
    profileinfo_url = "https://api.amazon.com/user/profile"
    
    h = httplib2.Http()
    headers={'x-amz-access-token': access_token}
    result = h.request(profileinfo_url, 'GET',headers=headers)[1]
    
    data = json.loads(result)
    login_session['provider'] = 'amazon'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['amazon_id'] = data["user_id"]

    
    # see if user exists
    user_id = getUserID(login_session['email'],'amazon')
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    
    flash("Now logged in as %s" % login_session['username'])
    return output

@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Validate state token    
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token  = request.data
    
    # Exchange client toke for long lived server-side token with 
    #access_token?grantype=fb_exchange_token&client_id={app-id}&client_secret
    #={app-secret}&fb_exchange_token={short-lived-token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    
    # see if user exists
    user_id = getUserID(login_session['email'],'facebook')
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    

    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/amazondisconnect')
def amazondisconnect():
    amazon_id=login_session['amazon_id']
    return "You have been logged out"

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Show all teams
@app.route('/')
@app.route('/team/')
def showTeams():
    """Render all team in database."""
    teams = session.query(Team).order_by(Team.created.desc()).all()
    #based on user the respective public/private page display
    if 'username' not in login_session:
        return render_template(
        'publichome.html',
        title='Home | FantasyFootball',
        year=datetime.now().year,
        teams=teams)
    else:
        return render_template(
        'home.html',
        title='Home | FantasyFootball',
        year=datetime.now().year,
        teams=teams)

# Create new team
@app.route('/team/new/',methods=['GET','POST'])
def newTeam():
    """ Display/Store new team details."""
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newTeam=Team(name=request.form['name'], 
            description=request.form['description'],user_id=login_session['user_id'] )
        session.add(newTeam)
        session.commit()
        flash('New Fantasy Team %s Created Successfully'% newTeam.name)
        return redirect(url_for('showTeams'))
    else:
        return render_template('newTeam.html',title='Add Team | FantasyFootball',year=datetime.now().year)
        
# Show json stucture of teams
@app.route('/team/json')
def teamsJSON():
    """Render all team in database."""
    list = []
    teams = session.query(Team).order_by(asc(Team.name))
    for t in teams:
        players = session.query(Player).filter_by(team_id=t.id).all()
        size=len(players)
        s="["
        count=0
        for p in players:
            count+=1
            s += str(p.serialize)
            if size != count:
                s += ","
        s += "]"
        
        list.append({"name": t.name,
            "id": t.id,
            "description": t.description,
            "players": s
            })
        
    return jsonify({"teams" : list})    

#present XML structure of teams 
@app.route('/team/xml/')
def teamsXML():
    teams=session.query(Team).all()
    players=session.query(Player).all()
    #return XML with appropriate mime type
    return Response(generate_xml(teams,players), mimetype='application/xml')

#show anything and everything about specific team
@app.route('/team/<int:team_id>/')
def showTeam(team_id):
    """Renders a specific team"""
    team = session.query(Team).filter_by(id=team_id).one()
    players = session.query(Player).filter_by(team_id=team_id).all()
    if 'username' not in login_session:
        return render_template('publicteam.html',title='Team | FantasyFootball',year=datetime.now().year, team=team, players=players)
    else:
        return render_template('team.html',title='Team | FantasyFootball',year=datetime.now().year, team=team, players=players)
        

#Edit a team
@app.route('/team/<int:team_id>/edit/',methods=['GET','POST'])
def editTeam(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    team=session.query(Team).filter_by(id=team_id).one()
    if team.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this team. Please create your personal team in order to edit.');history.back();}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            team.name = request.form['name']
        if request.form['description']:
            team.description = request.form['description']
        session.add(team)
        session.commit()
        flash('Successfully Edited team %s' % team.name)
        return redirect(url_for('showTeams'))
    else:
        return render_template('editTeam.html',title='Edit Team | FantasyFootball',year=datetime.now().year,team=team)

#Delete a team
@app.route('/team/<int:team_id>/delete/',methods=['GET','POST'])
def deleteTeam(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    team=session.query(Team).filter_by(id=team_id).one()
    if team.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this team. Please create your own team in order to delete.');history.back();}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        players=session.query(Player).all()
        for p in players:
            if p.snap_url:
                #remove snap from folder
                os.remove(APP_ROOT + player.snap_url)            
            session.delete(p)
            session.commit()
        session.delete(team)
        session.commit()
        flash('Successfully Deleted team %s' % team.name)        
        return redirect(url_for('showTeams'))
    else:
        return render_template('deleteTeam.html',title='Delete Team | FantasyFootball',year=datetime.now().year,team=team)


#function that checks the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Create new player  
@app.route('/team/<int:team_id>/player/new/',methods=['GET','POST'])
def newPlayer(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    team=session.query(Team).filter_by(id=team_id).one()
    if team.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to add player. Please create your own team in order to add player.');history.back();}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        snap_url = file_save(request.files['snap'])
        newPlayer = Player(name = request.form['name'], position
        = request.form['position'], description = request.form['description'],
        team_id = team_id, snap_url=snap_url,user_id=team.user_id)  
        session.add(newPlayer) 
        session.commit()
        
        return redirect(url_for('showTeam',team_id=team_id))        
    else:
        return render_template('newPlayer.html', title='Add Player | FantasyFootball',year=datetime.now().year,team_id=team_id) 


# Edit a player
@app.route('/team/<int:team_id>/player/<int:player_id>/edit/', methods=['GET', 'POST'])
def editPlayer(team_id, player_id):
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()
    player = session.query(Player).filter_by(id=player_id).one()
    if team.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit player. Please create your own team in order to add/edit player.');history.back();}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            player.name = request.form['name']
        if request.form['description']:
            player.description = request.form['description']
        if request.form['position']:
            player.position = request.form['position']
        if request.files['snap']:
            snap_url = file_save(request.files['snap'])
            player.snap_url=snap_url
        session.add(player)
        session.commit()
        flash('Player Successfully Edited')
        return redirect(url_for('showTeam', team_id=team_id))
    else:
        return render_template('editPlayer.html',title='Edit Player | FantasyFootball',year=datetime.now().year, team_id=team_id, 
            player_id = player_id, player=player)


# Delete a player
@app.route('/team/<int:team_id>/player/<int:player_id>/delete/', methods=['GET', 'POST'])
def deletePlayer(team_id, player_id):
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()
    player = session.query(Player).filter_by(id=player_id).one()
    if team.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete player. Please create your own team in order to add/edit/delete player.');history.back();}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if player.snap_url:
            #remove snap from folder
            os.remove(APP_ROOT + player.snap_url)
            #s.remove(os.path.join(APP_ROOT,player.snap_url))
            #os.remove(os.path.join(app.config['UPLOAD_FOLDER'], player.snap_url))
        session.delete(player)
        session.commit()
        flash('Player Successfully Deleted')
        return redirect(url_for('showTeam', team_id=team_id))
    else:         
        return render_template('deletePlayer.html',title='Delete Player | FantasyFootball',year=datetime.now().year, player=player)

#helper function to save file on server
def file_save(file):
    snap_url = ''    
    if file and allowed_file(file.filename):
        #remove unnecessary character out of filename
        filename = secure_filename(file.filename)
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        #hard coding can't find any otherway to retrieve path
        snap_url= '/static/snaps/' +file.filename
    else:
        flash("Not a valid snap file %s." % file.filename)
    return snap_url


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'],provider=login_session['provider'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email'],
        provider=login_session['provider']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email,provider):
    try:
        user = session.query(User).filter_by(email=email,provider=provider).one()
        return user.id
    except:
        return None