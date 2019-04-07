#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import re
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, Blueprint, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = 'secretkey'

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://zz2598:31415926@34.73.21.127/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

# error handling
error_pages = Blueprint('error_pages',__name__)

@error_pages.app_errorhandler(404)
def error_404(error):
    '''
    Error for pages not found.
    '''
    return render_template('404.html'), 404

@error_pages.app_errorhandler(403)
def error_403(error):
    '''
    Error for trying to access something which is forbidden.

    '''

    return render_template('403.html'), 403

app.register_blueprint(error_pages)

@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT teamname FROM team")
  # names = []
  # for result in cursor:
  #   names.append(result['teamname'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
from Forms import query_players_Form, query_teams_Form, query_venues_Form, query_games_Form, add_player_Form, add_game_Form
import time

@app.route('/query_players', methods=['GET', 'POST'])
def query_players():
    flag_exist = False
    cannot_find = False
    player_info = {}
    form = query_players_Form()
    cursor = g.conn.execute("select playername from player;")
    player_names = []
    for result in cursor:
      player_names.append(result['playername'])  # can also be accessed using result[0]
    cursor.close()
    time.sleep(0.005)
    if form.validate_on_submit():
        name = form.name.data
        print name
        cursor = g.conn.execute("select P.playerid from player P where P.playername='{}';".format(name))
        player_ids = []
        print cursor
        for result in cursor:
          player_ids.append(result['playerid'])  # can also be accessed using result[0]
        cursor.close()
        # all players in our database
        print len(player_ids), player_ids
        if len(player_ids) != 0:
            flag_exist = True
            cursor = g.conn.execute("select T.teamname from team T inner join membership M on T.teamid=M.teamid where M.playerid='{}' and M.teamid=T.teamid;".format(player_ids[0]))
            team_names = []
            print cursor
            for result in cursor:
              team_names.append(result['teamname'])  # can also be accessed using result[0]
            cursor.close()
            time.sleep(0.005)
            print len(team_names), team_names
            for team in team_names:
                # find all the game the team is involved
                print team
                query = ("WITH N AS ((select PV.home_teamid as H_ID, PV.away_teamid as A_ID from team T, play_versus PV where T.teamname='%s' "
                         "and (T.teamid = PV.home_teamid or T.teamid = PV.away_teamid))),N2 AS (select T2.teamname AS H_name, N.A_ID AS A_ID "
                         "from N inner join Team T2 on N.H_ID=T2.teamid), N3 AS (select N2.H_name AS H_name, T3.teamname AS A_name from N2 "
                         "inner join Team T3 on N2.A_ID=T3.teamid) select N3.H_name, N3.A_name from N3;") %(team)
                print 'the query is: ', query
                cursor = g.conn.execute(query)
                H_A_names = []
                print cursor
                for result in cursor:
                  H_A_names.append([result['h_name'],result['a_name']])  # can also be accessed using result[0]
                cursor.close()
                time.sleep(0.005)
                print H_A_names
                player_info[team] = H_A_names
            print player_info
        else:
            cannot_find = True
        return render_template("query_players.html", form=form, flag_exist=flag_exist, player_info=player_info, player_names=player_names, cannot_find = cannot_find)

    return render_template("query_players.html", form=form, flag_exist=flag_exist, player_info=player_info, player_names=player_names, cannot_find = cannot_find)

@app.route('/query_teams', methods=['GET','POST'])
def query_teams():
    flag_exist = False
    cannot_find = False
    team_info = {}
    form = query_teams_Form()
    cursor = g.conn.execute("select teamname from team;")
    team_names = []
    for result in cursor:
      team_names.append(result['teamname'])  # can also be accessed using result[0]
    cursor.close()
    time.sleep(0.005)
    if form.validate_on_submit():
        name = form.name.data
        print name
        cursor = g.conn.execute("select T.teamid from team T where T.teamname='{}';".format(name))
        team_ids = []
        print cursor
        for result in cursor:
          team_ids.append(result['teamid'])  # can also be accessed using result[0]
        cursor.close()
        time.sleep(0.005)
        # all teams in our database
        print len(team_ids), team_ids
        if len(team_ids) != 0:
            team = name
            flag_exist = True
            query = ("WITH N AS ((select PV.home_teamid as H_ID, PV.away_teamid as A_ID from team T, play_versus PV where T.teamname='%s' "
                     "and (T.teamid = PV.home_teamid or T.teamid = PV.away_teamid))),N2 AS (select T2.teamname AS H_name, N.A_ID AS A_ID "
                     "from N inner join Team T2 on N.H_ID=T2.teamid), N3 AS (select N2.H_name AS H_name, T3.teamname AS A_name from N2 "
                     "inner join Team T3 on N2.A_ID=T3.teamid) select N3.H_name, N3.A_name from N3;") %(team)
            print 'the query is: ', query
            cursor = g.conn.execute(query)
            H_A_names = []
            print cursor
            for result in cursor:
              H_A_names.append([result['h_name'],result['a_name']])  # can also be accessed using result[0]
            cursor.close()
            time.sleep(0.00001)
            print H_A_names
            # get the team_members
            team_members = []
            query = "select P.playername from (membership M inner join team T on M.teamid=T.teamid) inner join player P on M.playerid=P.playerid where T.teamname='%s';" %team
            cursor=g.conn.execute(query)
            for result in cursor:
                team_members.append(result['playername'])
            cursor.close()
            time.sleep(0.00001)
            team_info[team] = [H_A_names, team_members]
            print team_info

        else:
            cannot_find = True

        return render_template("query_teams.html", form=form, flag_exist=flag_exist, team_info=team_info, team_names=team_names, cannot_find = cannot_find)

    return render_template("query_teams.html", form=form, flag_exist=flag_exist, team_info=team_info, team_names=team_names, cannot_find = cannot_find)

@app.route('/query_games',methods=['GET','POST'])
def query_games():
    flag_exist = False
    cannot_find = False
    game_info = {}
    form = query_games_Form()
    cursor = g.conn.execute("select T1.teamname as home_teamname, T2.teamname as away_teamname from (play_versus PV inner join team T1 ON PV.home_teamid=T1.teamid) inner join team T2 ON PV.away_teamid=T2.teamid;")
    games = []
    for result in cursor:
      games.append([result['home_teamname'], result['away_teamname']])  # can also be accessed using result[0]
    cursor.close()
    time.sleep(0.005)
    if form.validate_on_submit():
        home_name = form.home_name.data
        away_name = form.away_name.data
        print home_name, away_name


        # all information about games in a particular venue
        query =  ("select G.date, T1.teamname as home_teamname,T2.teamname as away_teamname,PRHI.winner, S1.runnumber as home_runnumber, S1.errornumber as home_errornumber, "
                  "S1.hitnumber as home_hitnumber,S2.runnumber as away_runnumber, S2.errornumber as away_errornumber, "
                  "S2.hitnumber as away_hitnumber, E.weather as weather, E.day_or_night as day_or_night "
                  "from (((((team T1 inner join play_result_held_in PRHI ON T1.teamid=PRHI.home_teamid and T1.teamname='%s') "
                  "inner join team T2 ON T2.teamid=PRHI.away_teamid and T2.teamname='%s') "
                  "inner join scoredetail S1 on PRHI.home_scoreid=S1.scoreid) inner join scoredetail S2 on "
                  "PRHI.away_scoreid=S2.scoreid) inner join environment E on E.environmentid=PRHI.environmentid) inner join game G on G.gameid=PRHI.gameid ;") %(home_name, away_name)
        print 'the query is: ',query
        cursor = g.conn.execute(query)
        teams = ()
        temp=[]
        details = []
        for result in cursor:
            temp = [result['home_teamname'], result['away_teamname']]
            teams = tuple(temp)
            details=[result['date'], result['winner'], result['home_runnumber'],result['home_errornumber'],result['home_hitnumber'], \
                            result['away_runnumber'],result['away_errornumber'],result['away_hitnumber'], result['weather'], \
                             result['day_or_night']]
            game_info[teams]=details
        cursor.close()
        time.sleep(0.005)

        print len(game_info), game_info
        if len(game_info) != 0:
            flag_exist = True
        else:
            cannot_find = True
        return render_template("query_games.html", form=form, flag_exist=flag_exist, game_info=game_info, games=games, cannot_find=cannot_find)

    return render_template("query_games.html", form=form, flag_exist=flag_exist, game_info=game_info, games=games, cannot_find = cannot_find)



@app.route('/query_venues',methods=['GET','POST'])
def query_venues():
    flag_exist = False
    cannot_find = False
    venue_info = {}
    form = query_venues_Form()
    cursor = g.conn.execute("select distinct venue from environment;")
    venues = []
    for result in cursor:
      venues.append(result['venue'])  # can also be accessed using result[0]
    cursor.close()
    time.sleep(0.005)
    if form.validate_on_submit():
        name = form.name.data
        print name
        # all information about games in a particular venue
        query =  ("WITH N AS(SELECT E.environmentid as environmentid FROM environment E WHERE E.venue='%s') "
                  "select G.date, T1.teamname as home_teamname, T2.teamname as away_teamname, PRHI.winner as winner, "
                  "S1.runnumber as home_runnumber, S1.errornumber as home_errornumber, S1.hitnumber as home_hitnumber,"
                  "S2.runnumber as away_runnumber, S2.errornumber as away_errornumber, S2.hitnumber as away_hitnumber, "
                  "E.weather, E.day_or_night from ((((((play_result_held_in PRHI inner join N "
                  "on PRHI.environmentid=N.environmentid) inner join team T1 on T1.teamid=PRHI.home_teamid) inner join "
                  "team T2 on T2.teamid=PRHI.away_teamid) inner join scoredetail S1 on PRHI.home_scoreid=S1.scoreid) "
                  "inner join scoredetail S2 on PRHI.away_scoreid=S2.scoreid) inner join environment E on E.environmentid"
                  "=N.environmentid) inner join game G on G.gameid=PRHI.gameid;") % name
        print 'the query is: ',query
        cursor = g.conn.execute(query)
        teams = ()
        temp=[]
        details = []
        for result in cursor:
            temp = [result['home_teamname'], result['away_teamname']]
            teams = tuple(temp)
            details=[result['date'], result['winner'], result['home_runnumber'],result['home_errornumber'],result['home_hitnumber'], \
                            result['away_runnumber'],result['away_errornumber'],result['away_hitnumber'], result['weather'], \
                             result['day_or_night']]
            venue_info[teams]=details
        cursor.close()
        time.sleep(0.005)

        print len(venue_info), venue_info
        if len(venue_info) != 0:
            flag_exist = True
        else:
            cannot_find = True
        return render_template("query_venues.html", form=form, flag_exist=flag_exist, venue_info=venue_info, venues=venues, cannot_find=cannot_find)

    return render_template("query_venues.html", form=form, flag_exist=flag_exist, venue_info=venue_info, venues=venues, cannot_find = cannot_find)

@app.route('/add_player', methods=['GET', 'POST'])
def add_player():

    already_exist = False
    new_team = False
    auxiliary_flag = False
    form = add_player_Form()
    cursor = g.conn.execute("select playername from player;")
    player_names = []
    for result in cursor:
      player_names.append(result['playername'])  # can also be accessed using result[0]
    cursor.close()
    time.sleep(0.005)
    if form.validate_on_submit():
        player_name = form.player_name.data
        #  if the player aleady  exits
        if u'{}'.format(player_name) in player_names:
            already_exist = True
            print 'the player {} already exits in our database'.format(player_name)
        else:
            team_name = form.team_name.data
            # To see if the team already exists
            cursor = g.conn.execute("select count (teamname) as team_count from team where teamname='{}';".format(team_name))
            team_counts = []
            print cursor
            for result in cursor:
              team_counts.append(result['team_count'])  # can also be accessed using result[0]
            cursor.close()
            time.sleep(0.005)
            print team_counts
            # team_counts[0] is the number of existence of the team in database
            if (team_counts[0] == 0):
                new_team = True
                g.conn.execute("insert into team(teamname) values ('%s');" %(team_name))
                print ('created new team record!')
                time.sleep(0.005)
            else:
                auxiliary_flag = True
            g.conn.execute("insert into player(playername) values ('%s');" %(player_name))
            print ('created new player record!')
            time.sleep(0.005)

            # get the team id, for future use of inserting a membership tuple
            cursor = g.conn.execute("select teamid from team where teamname='{}';".format(team_name))
            team_ids = []
            print cursor
            for result in cursor:
              team_ids.append(result['teamid'])  # can also be accessed using result[0]
            cursor.close()
            time.sleep(0.005)
            teamid = team_ids[0]
            print team_ids, teamid

            # get the team id, for future use of inserting a membership tuple
            cursor = g.conn.execute("select playerid from player where playername='{}';".format(player_name))
            player_ids = []
            print cursor
            for result in cursor:
              player_ids.append(result['playerid'])  # can also be accessed using result[0]
            cursor.close()
            time.sleep(0.005)
            playerid = player_ids[0]
            print player_ids, playerid

            g.conn.execute("insert into membership(teamid,playerid) values ('%s','%s');" %(teamid,playerid))
            print ('created new membership record!')
            time.sleep(0.005)


        return render_template("add_player.html", form=form, already_exist=already_exist, new_team = new_team, player_names=player_names, auxiliary_flag=auxiliary_flag)

    return render_template("add_player.html", form = form, already_exist=already_exist, new_team = new_team, player_names=player_names, auxiliary_flag=auxiliary_flag)


@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    already_exist = False
    success_flag = False
    form = add_game_Form()
    cursor = g.conn.execute("select T1.teamname as home_teamname, T2.teamname as away_teamname from (play_versus PV inner join team T1 ON PV.home_teamid=T1.teamid) inner join team T2 ON PV.away_teamid=T2.teamid;")
    games = []
    for result in cursor:
      games.append([result['home_teamname'], result['away_teamname']])  # can also be accessed using result[0]
    cursor.close()
    time.sleep(0.00001)
    print 'hi iam before validate on submit'
    if form.validate_on_submit():
        date = form.date.data
        home_teamname = form.home_teamname.data
        away_teamname = form.away_teamname.data
        winner = form.winner.data
        home_runnumber = form.home_runnumber.data
        home_errornumber = form.home_errornumber.data
        home_hitnumber = form.home_hitnumber.data
        away_runnumber = form.away_runnumber.data
        away_errornumber = form.away_errornumber.data
        away_hitnumber = form.away_hitnumber.data
        weather = form.weather.data
        venue = form.venue.data
        day_or_night = form.day_or_night.data
        print 'Hi iam in validate on submit'
        # all scores must be integers
        temp_list = [home_hitnumber, home_runnumber, home_errornumber, away_hitnumber, away_runnumber, away_errornumber]
        for i in temp_list:
            print not bool(re.search(r'^[0-9]+$', str(i)))
            if not bool(re.search(r'^[0-9]+$', str(i))):
                flash('Please enter valid input. Score number must be integers.')
                print 'Hi i am before return'
                return render_template("add_game.html", form=form, already_exist=already_exist, success_flag=success_flag, games=games)
        # create home_/away_team if it does not exist, get the home_teamid and away_teamid
        temp = [home_teamname, away_teamname]
        team_ids = []
        for i in temp:
            cursor = g.conn.execute("select teamid from team where teamname='%s';" %(i))
            ids = []
            for result in cursor:
              ids.append(result['teamid'])  # can also be accessed using result[0]
            cursor.close()
            time.sleep(0.00001)
            # if the team does not exist
            if len(ids) == 0:
                g.conn.execute("insert into team(name) values ('%s')" %(i))
                time.sleep(0.00001)
                # get the teamid
                cursor = g.conn.execute("select teamid from team where teamname='%s';" %(i))
                ids = []
                for result in cursor:
                  ids.append(result['teamid'])  # can also be accessed using result[0]
                cursor.close()
                time.sleep(0.00001)
                print 'the team id is: ', ids[0]
                team_ids.append(ids[0])
            else:
                print 'the team id is: ', ids[0]
                team_ids.append(ids[0])

        # create scoredetail tuple if it does not exist, get the scoreid
        temp=[[home_runnumber, home_errornumber, home_hitnumber],[away_runnumber, away_errornumber, away_hitnumber]]
        score_ids=[]
        for i in temp:
            cursor = g.conn.execute("select scoreid from scoredetail where runnumber=%d and errornumber=%d and hitnumber=%d;" %(int(i[0]), int(i[1]), int(i[2])))
            ids = []
            for result in cursor:
              ids.append(result['scoreid'])
            cursor.close()
            time.sleep(0.00001)
            # if the team does not exist
            if len(ids) == 0:
                g.conn.execute("insert into scoredetail(runnumber, errornumber, hitnumber) values (%d,%d,%d)" %(int(i[0]), int(i[1]), int(i[2])))
                time.sleep(0.00001)
                # get the teamid
                cursor = g.conn.execute("select scoreid from scoredetail where runnumber=%d and errornumber=%d and hitnumber=%d;" %(int(i[0]), int(i[1]), int(i[2])))
                ids = []
                for result in cursor:
                  ids.append(result['scoreid'])
                cursor.close()
                time.sleep(0.00001)
                print 'the score id is: ', ids[0]
                score_ids.append(ids[0])
            else:
                print 'the score id is: ', ids[0]
                score_ids.append(ids[0])

        # create environment tuple if it does not exist, get the environmentid
        # if weather is unknown, insert null value into database
        print "weather == 'Unknown': ", weather=='Unknown'
        if weather == 'Unknown':
            cursor = g.conn.execute("select environmentid from environment where venue='%s' and day_or_night='%s';" %(venue, day_or_night))
        else:
            cursor = g.conn.execute("select environmentid from environment where weather='%s' and venue='%s' and day_or_night='%s';" %(weather, venue, day_or_night))
        ids = []
        for result in cursor:
          ids.append(result['environmentid'])
        cursor.close()
        time.sleep(0.00001)
        # if the environment tuple does not exist
        if len(ids) == 0:
            if weather == 'Unknown':
                g.conn.execute("insert into environment(weather, venue, day_or_night) values (NULL,'%s','%s')" %(venue, day_or_night))
            else:
                g.conn.execute("insert into environment(weather, venue, day_or_night) values ('%s','%s','%s')" %(weather, venue, day_or_night))
            time.sleep(0.00001)
            # then get the id

            if weather == 'Unknown':
                cursor = g.conn.execute("select environmentid from environment where venue='%s' and day_or_night='%s';" %(venue, day_or_night))
            else:
                cursor = g.conn.execute("select environmentid from environment where weather='%s' and venue='%s' and day_or_night='%s';" %(weather, venue, day_or_night))
            ids = []
            for result in cursor:
              ids.append(result['environmentid'])
            cursor.close()
            time.sleep(0.00001)
            print 'environment id is: ', ids[0]
            environmentid = ids[0]
        else:
            print 'environment id is: ', ids[0]
            environmentid = ids[0]

        # insert into table play_versus, if the record does not exist
        pv_counts=[]
        cursor = g.conn.execute("select count (*) as pv_count from play_versus where home_teamid=%d and away_teamid=%d" %(team_ids[0], team_ids[1]))
        for result in cursor:
            pv_counts.append(result['pv_count'])
        cursor.close()
        time.sleep(0.00001)
        print pv_counts[0]
        # if the home_team pair does not exist in database, we need to insert this tuple
        if pv_counts[0] == 0:
            g.conn.execute("insert into play_versus(home_teamid,away_teamid) VALUES (%d,%d)" %(team_ids[0],team_ids[1]))
            time.sleep(0.00001)

        # insert into table score_versus, if the record does not exist
        sv_counts=[]
        cursor = g.conn.execute("select count (*) as sv_count from score_versus where home_scoreid=%d and away_scoreid=%d" %(score_ids[0], score_ids[1]))
        for result in cursor:
            sv_counts.append(result['sv_count'])
        cursor.close()
        time.sleep(0.00001)
        print sv_counts[0]
        # if the home_team pair does not exist in database, we need to insert this tuple
        if sv_counts[0] == 0:
            g.conn.execute("insert into score_versus(home_scoreid,away_scoreid) VALUES (%d,%d)" %(score_ids[0],score_ids[1]))
            time.sleep(0.00001)


        # insert into table play_result_held_in and game, if the record does not exist
        # check if the record exists
        prhi_counts=[]
        query = ("select count (*) as prhi_count from play_result_held_in where winner='%s' and home_teamid=%d and away_teamid=%d and "
                 "home_scoreid=%d and away_scoreid=%d and environmentid=%d;") %(winner, team_ids[0], team_ids[1], score_ids[0],score_ids[1], environmentid)
        cursor = g.conn.execute(query)
        for result in cursor:
            prhi_counts.append(result['prhi_count'])
        cursor.close()
        time.sleep(0.00001)
        print prhi_counts[0]
        # if the game record does not exist in database, we need to insert this tuple to play_result_held_in and game
        if prhi_counts[0] == 0:
            # insert into game table
            g.conn.execute("insert into game(date) values ('{}');" .format(str(date)))
            # get the game id
            game_ids=[]
            cursor = g.conn.execute('select max(gameid) as game_id from game;')
            for result in cursor:
                game_ids.append(result['game_id'])
            cursor.close()
            game_id = game_ids[0]
            time.sleep(0.00001)

            # insert tuple into play_result_held_in
            query=("insert into play_result_held_in(gameid, winner,home_teamid,away_teamid,home_scoreid,away_scoreid,environmentid) "
                    "VALUES (%d,'%s',%d,%d,%d,%d,%d);") %(game_id,winner,team_ids[0],team_ids[1],score_ids[0],score_ids[1],environmentid)
            g.conn.execute(query)
            time.sleep(0.00001)

            success_flag = True
        else:
            already_exist = True
        return render_template("add_game.html", form=form, already_exist=already_exist, success_flag=success_flag,games=games)
    return render_template("add_game.html", form=form, already_exist=already_exist, success_flag=success_flag,games=games)

# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   g.conn.execute("INSERT INTO test(name) VALUES ('{}');".format(name))
#   return redirect('/')


# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)





  run()
