from flask import Flask, render_template, request, redirect, url_for, jsonify, g, Response
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy.pool import NullPool
from sqlalchemy import *

DB_USER = "yz3423"
DB_PASSWORD = "j88dpf9i"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASEURI
db = SQLAlchemy(app)
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
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
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
    cursor = g.conn.execute(
    """
    SELECT Event.eid, Event.location, Event.food_info, Event.title, Event.abstract, Event.begin_time, 
    Event.end_time, Organization.otitle, Researcher.rname, Department.dname, Department.iid
    FROM HOLD, EVENT, Organization, Participate, Researcher, Affiliate_with_department, Department
    WHERE Hold.eid = Event.eid
    AND Organization.oid = Hold.oid
    AND Participate.hid = Hold.hid
    AND Researcher.rid = Participate.rid
    AND Affiliate_with_department.rid = Researcher.rid
    AND Department.did = Affiliate_with_department.did
    ORDER BY EVENT.begin_time DESC;
    """)
    posts = []
    for r in cursor:
        posts.append(r)
    cursor.close()
    return render_template('index.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<int:post_eid>')
def post(post_eid):
    cmd = 'SELECT Event.eid, Event.location, Event.food_info, Event.title, Event.abstract, Event.begin_time, Event.end_time, Organization.otitle, Researcher.rname, Department.dname, Department.iid, Institution.iname FROM HOLD, EVENT, Organization, Participate, Researcher, Affiliate_with_department, Department, Institution WHERE Hold.eid = Event.eid AND Organization.oid = Hold.oid AND Participate.hid = Hold.hid AND Researcher.rid = Participate.rid AND Affiliate_with_department.rid = Researcher.rid AND Department.did = Affiliate_with_department.did AND Institution.iid = Department.iid AND Event.eid = (:post_eid)';
    cursor = g.conn.execute(text(cmd), post_eid = post_eid);
    post = []
    for r in cursor:
        post.append(r)
    cursor.close()
    return render_template('post.html', post = post[0])

@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/search_index', methods=['GET', 'POST'])
def search_index():
    drop_posts = 'DROP TABLE IF EXISTS Posts';
    create_posts_from_temp = 'CREATE TABLE Posts AS SELECT * FROM Temp';
    drop_temp = 'DROP TABLE IF EXISTS Temp';

 
    cursor = g.conn.execute(text(drop_posts));
    base_posts = 'CREATE TABLE POSTS AS SELECT DISTINCT Event.eid, Event.location, Event.food_info, Event.title, Event.abstract, Event.begin_time, Event.end_time, Event.target_audience, Organization.otitle, Researcher.rname, Researcher.gender, Researcher.status,Department.dname, Institution.iname, Area.aname FROM HOLD, EVENT, Organization, Participate, Researcher, Affiliate_with_department, Department, Area, Affiliate_with_organization, Institution, Label WHERE Hold.eid = Event.eid AND Organization.oid = Hold.oid AND Participate.hid = Hold.hid AND Researcher.rid = Participate.rid AND Affiliate_with_department.rid = Researcher.rid AND Department.did = Affiliate_with_department.did AND Institution.iid = Department.iid AND Label.eid = Event.eid AND Area.aid = Label.aid ORDER BY Event.begin_time DESC';
    cursor = g.conn.execute(text(base_posts));


    title = request.form['title']
    print(title)
    if title:
        cursor = g.conn.execute(text(drop_temp));
        create_temp = "CREATE TABLE Temp AS SELECT * FROM Posts WHERE title LIKE (:title)";
        cursor = g.conn.execute(text(create_temp), title = title);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    begin_time = request.form['begin_time']
    if begin_time:
        cursor = g.conn.execute(text(drop_temp));
        create_temp = 'CREATE TABLE Temp AS SELECT * FROM Posts WHERE begin_time >= (:begin_time)';
        cursor = g.conn.execute(text(create_temp), begin_time = begin_time);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    end_time = request.form['end_time']
    if end_time:
        cursor = g.conn.execute(text(drop_temp));
        create_temp = 'CREATE TABLE Temp AS SELECT * FROM Posts WHERE end_time <= (:end_time)';
        cursor = g.conn.execute(text(create_temp), end_time = end_time);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));


    location = request.form['location']
    if location:
        cursor = g.conn.execute(text(drop_temp));
        create_temp = 'CREATE TABLE Temp AS SELECT * FROM Posts WHERE location = (:location)';
        cursor = g.conn.execute(text(create_temp), location = location);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));
    
    rname = request.form['rname']
    if rname:
        cursor = g.conn.execute(text(drop_temp));
        create_temp =  "CREATE TABLE Temp AS SELECT * FROM Posts WHERE rname = (:rname)";
        cursor = g.conn.execute(text(create_temp), rname = rname);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));


    otitle = request.form['otitle']
    if otitle:
        cursor = g.conn.execute(text(drop_temp));
        create_temp =  'CREATE TABLE Temp AS SELECT * FROM Posts WHERE otitle = (:otitle)';
        cursor = g.conn.execute(text(create_temp), otitle = otitle);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    iname = request.form['iname']
    if iname:
        cursor = g.conn.execute(text(drop_temp));
        create_temp =  'CREATE TABLE Temp AS SELECT * FROM Posts WHERE iname = (:iname)';
        cursor = g.conn.execute(text(create_temp), iname = iname);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    aname = request.form['aname']
    if aname:
        cursor = g.conn.execute(text(drop_temp));
        create_temp =  "CREATE TABLE Temp AS SELECT * FROM Posts WHERE aname = (:aname)";
        cursor = g.conn.execute(text(create_temp), aname = aname);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    dname = request.form['dname']
    if dname:
        cursor = g.conn.execute(text(drop_temp));
        create_temp =  'CREATE TABLE Temp AS SELECT * FROM Posts WHERE dname = (:dname)';
        cursor = g.conn.execute(text(create_temp), dname = dname);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    target_audience = request.form['target_audience']
    if target_audience:
        cursor = g.conn.execute(text(drop_temp));
        create_temp =  'CREATE TABLE Temp AS SELECT * FROM Posts WHERE target_audience LIKE (:target_audience)';
        cursor = g.conn.execute(text(create_temp), target_audience = target_audience);
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    food_info = 'food_info' in request.form
    if 'food_info':  
        cursor = g.conn.execute(text(drop_temp));
        create_temp = "CREATE TABLE Temp AS SELECT * FROM Posts WHERE food_info IS NOT NULL AND food_info !=(:no) AND food_info != (:nno)";
        cursor = g.conn.execute(text(create_temp), no = "no", nno = "No");
        cursor = g.conn.execute(text(drop_posts));
        cursor = g.conn.execute(text(create_posts_from_temp));

    #tg_faculty = request.form['tg_faculty']
    #tg_pos = request.form['tg_pos']
    #tg_phd = request.form['tg_phd']
    #tg_ms = request.form['tg_ms']
    #tg_under = request.form['tg_under']
    #tg_visitor = request.form['tg_visitor']
    #title_list = ['faculty', 'pos', 'phd', 'ms', 'under', 'visit']
    #tg_list = ['tg_faculty', 'tg_pos', 'tg_phd', 'tg_ms', 'tg_under', 'tg_visitor'] 
    #lst_str = "WHERE"
    #for i in range(len(title_list)):
    #    if tg_list[i] in request.form:
    #        if i == 0:
    #            lst_str = lst_str + title_list[i] + "LIKE %'(:" + title_list[i] +")%'"
    #        lst_str = lst_str + "OR" + title_list[i] + "LIKE %'(:" + title_list[i] +")%'"

    #if lst_str != "WHERE":
    #    cursor = g.conn.execute(text(drop_temp));
    #    create_temp = 'CREATE TABLE Temp AS SELECT * FROM Posts' + lst_str;
    #    cursor = g.conn.execute(text(create_temp));
    #    cursor = g.conn.execute(text(drop_posts));
    #    cursor = g.conn.execute(text(create_posts_from_temp));


    #st_faculty = request.form['st_faculty']
    #st_pos = request.form['st_pos']
    #st_phd = request.form['st_phd']
    #st_ms = request.form['st_ms']
    #st_under = request.form['st_under']
    #st_visitor = request.form['st_visitor']
    #lst_str = "WHERE"
    #ind = 0
    #for i in ['st_faculty', 'st_pos', 'st_phd', 'st_ms', 'st_under', 'st_visitor']:
    #    if i in request.form:
    #        if ind == 0:
    #            ind = ind + 1
    #            lst_str = lst_str + str(i) + "LIKE %'(:" + str(i) +")%'"
    #        lst_str = lst_str + "OR" + str(i)+ "LIKE %'(:" + str(i) +")%'"

    #if lst_str != "WHERE":
    #    cursor = g.conn.execute(text(drop_temp));
    #    create_temp = 'CREATE TABLE Temp AS SELECT * FROM Posts' + lst_str;
    #    cursor = g.conn.execute(text(create_temp));
    #    cursor = g.conn.execute(text(drop_posts));
    #    cursor = g.conn.execute(text(create_posts_from_temp));


    cursor = g.conn.execute("""SELECT DISTINCT * FROM Posts ORDER BY begin_time DESC;""")
    posts = []
    for r in cursor:
        posts.append(r)
    cursor.close()
    return render_template('search_index.html', posts = posts)  


@app.route('/search_add')
def search_add():
    return render_template('search_add.html')

@app.route('/addpost', methods=['POST'])
def addpost():
    location = request.form['location']
    food_info = request.form['food_info']
    title = request.form['title']
    abstract = request.form['abstract']
    begin_time = request.form['begin_time']
    end_time = request.form['end_time']
    target_audience = request.form['target_audience']
    cmd1 = 'INSERT INTO Event(location, food_info, title, abstract, begin_time, end_time, target_audience) Values ((:location), (:food_info), (:title), (:abstract), (:begin_time), (:end_time), (:target_audience))';
    cursor = g.conn.execute(text(cmd1), location = location, food_info = food_info, title = title, abstract = abstract, begin_time = begin_time, end_time = end_time, target_audience = target_audience);
    cursor_eid = g.conn.execute("""SELECT MAX(eid) FROM Event;""")
    for r in cursor_eid:
        eid = int(r[0])
    cursor.close()


    rname = request.form['rname']
    gender = request.form['gender']
    status = request.form['status']
    cmd3 = 'INSERT INTO Researcher(rname, gender, status) Values ((:rname),(:gender), (:status))';
    cursor = g.conn.execute(text(cmd3), rname = rname, gender = gender,  status = status);
    cursor_rid = g.conn.execute("""SELECT MAX(rid) FROM Researcher;""")
    for r in cursor_rid:
        rid = int(r[0])
    cursor.close()


    aname = request.form['aname']
    #try_aid = 'SELECT aid FROM Area WHERE aname = (:aname)';
    #cursor = g.conn.execute(text(try_aid), aname = aname);
    #aid_list = []
    #for r in cursor:
    #    aid_list.append(int(r[0]))
    #if len(aid_list) > 0:
    #    aid = aid_list[0]
    #else:
    cmd2 = 'INSERT INTO Area(aname) Values (:aname)';
    cursor = g.conn.execute(text(cmd2), aname = aname);
    cursor_aid = g.conn.execute("""SELECT MAX(aid) FROM Area;""")
    for r in cursor_aid:
        aid = int(r[0])
    cursor.close()

    iname = request.form['iname']
    #try_iid = 'SELECT iid FROM Institution WHERE iname = (:iname)';
    #cursor = g.conn.execute(text(try_iid), iname = iname);
    #iid_list = []
    #for r in cursor:
    #    iid_list.append(int(r[0]))
    #if len(iid_list) > 0:
    #    iid = iid_list[0]
    #else:
    cmd4 = 'INSERT INTO Institution(iname) Values (:iname)';
    cursor = g.conn.execute(text(cmd4), iname = iname);
    cursor_iid = g.conn.execute("""SELECT MAX(iid) FROM Institution;""")
    for r in cursor_iid:
        iid = int(r[0])
    cursor.close()

 
    otitle = request.form['otitle']
    #try_oid = 'SELECT oid FROM Organization WHERE otitle = (:otitle)';
    #cursor = g.conn.execute(text(try_oid), otitle = otitle);
    #oid_list = []
    #for r in cursor:
    #    oid_list.append(int(r[0]))
    #if len(oid_list) > 0:
    #    oid = oid_list[0]
    #else:
    cmd5 = 'INSERT INTO Organization(iid, otitle) Values ((:iid), (:otitle))';
    cursor = g.conn.execute(text(cmd5), iid = iid, otitle = otitle);
    cursor_oid = g.conn.execute("""SELECT MAX(oid) FROM Organization;""")
    for r in cursor_oid:
        oid = int(r[0])
    cursor.close()


    cmd6 = 'INSERT INTO Hold(oid, eid) Values((:oid),(:eid))';
    cursor = g.conn.execute(text(cmd6), oid = oid, eid = eid);
    cursor_hid = g.conn.execute("""SELECT MAX(hid) FROM Hold;""")
    for r in cursor_hid:
        hid = int(r[0])
    cursor.close()

 
    cmd7 = 'INSERT INTO Participate(hid, rid) Values((:hid), (:rid))';
    cursor = g.conn.execute(text(cmd7), hid = hid, rid = rid);
    cursor.close() 
  
    dname = request.form['dname']
    #try_did = 'SELECT did FROM Department WHERE dname = (:dname)';
    #cursor = g.conn.execute(text(try_did), dname = dname);
    #did_list = []
    #for r in cursor:
    #    did_list.append(int(r[0]))
    #if len(did_list) > 0:
    #    did = did_list[0]
    #else:
    cmd8 = 'INSERT INTO Department(dname, iid) SELECT (:dname), (:iid)';
    cursor = g.conn.execute(text(cmd8), dname = dname, iid = iid);
    cursor_did = g.conn.execute("""SELECT MAX(did) FROM Department;""")
    for r in cursor_did:
        did = int(r[0])
    cursor.close()

    cmd9 = 'INSERT INTO Affiliate_with_department(did, rid) VALUES((:did),(:rid))';
    cursor = g.conn.execute(text(cmd9), did = did, rid = rid);
    cursor.close()
    

    cmd10 = 'INSERT INTO Affiliate_with_organization(oid,rid) VALUES((:oid), (:rid))';
    cursor = g.conn.execute(text(cmd10), oid = oid, rid = rid);
    cursor.close()

    cmd11 = 'INSERT INTO focus(aid,rid) VALUES((:aid), (:rid))';
    cursor = g.conn.execute(text(cmd11), aid = aid, rid = rid);
    cursor.close()

    cmd12 = 'INSERT INTO label(eid,aid) VALUES((:eid), (:aid))';
    cursor = g.conn.execute(text(cmd12), eid = eid, aid = aid);
    cursor.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, threaded=False)
