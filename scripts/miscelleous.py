 'mysql://root:mdclinicals@localhost/linh'



DATABASE_URL =  'postgres://postgres:mdclinicals@localhost/regulatory_docs'


postgres://edynzmbihsrqyi:cebba2154ce00a491dbc5615d1023335ad8aa2b1924a0cf9f32f7c8c28ecc655@ec2-99-80-170-190.eu-west-1.compute.amazonaws.com:5432/d9fbv65o7volfj

url(https://cms-static.wehaacdn.com/documentmedia-com/images/7-DMS-for-Compliance.1950.jpg) no-repeat;


CREATE TABLE User (ID SERIAL PRIMARY KEY, firstname VARCHAR(50),
                    lastname VARCHAR(50), company VARCHAR(50), country VARCHAR(50), 
                    email VARCHAR(50) unique, password VARCHAR(120), confirm_email BOOLEAN NOT NULL,
                    created_date DATE NOT NULL);


from flask_track_usage import TrackUsage
from flask_track_usage.storage.sql import SQLStorage

from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String

metadata_obj = MetaData()


pstorage = SQLStorage(db=db)
trk = TrackUsage(app, [pstorage])


from flask_track_usage import TrackUsage
from flask_track_usage.storage.sql import SQLStorage

pstorage = SQLStorage(db=db)
trk = TrackUsage(app, [pstorage])


Flask_usage = Table(
    "flask_usage",
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('url', String(128)),
    Column('ua_browser', String(16)),
    Column('ua_language', String(16)),
    Column('ua_platform', String(16)),
    Column('ua_version', String(16)),
    Column('blueprint', String(16)),
    Column('view_args', String(64)),
    Column('status', Integer),
    Column('xforwardedfor', String(64)),
    Column('authorization', BOOLEAN),
    Column('ip_info', String(1024)),
    Column('path', String(128)),
    Column('speed', Float),
    Column('datatime', DateTime),
    Column('username', String(128)),
    Column('track_var', String(128)),
 )


class flask_usage(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), nullable=False)
    ua_browser = db.Column(db.String(16))
    ua_language = db.Column(db.String(16))
    ua_platform = db.Column(db.String(16))
    ua_version = db.Column(db.String(16))
    blueprint = db.Column(db.String(16))
    view_args = db.Column(db.String(64))
    status = db.Column(db.Integer)
    xforwardedfor = db.Column(db.String(24))
    authorization = db.Column(db.Boolean, default=False)
    ip_info = db.Column(db.String(1024))
    path = db.Column(db.String(1024))
    speed = db.Column(db.Float)
    datatime = db.Column(DateTime, default=datetime.datetime.utcnow)
    username = db.Column(db.String(128))
    track_var = db.Column(db.String(128))



#return Users.get(int(user_id))
cursor = conn.cursor()
cursor.execute("Select * from Users where id=%s", (user_id,))

new_user = Users(firstname=user_exists[1],
                             lastname=user_exists[2],
                             company=user_exists[3],
                             country=user_exists[4],
                             email=user_exists[5],
                             password=user_exists[6],
                             confirm_email=user_exists[7]
                             )
new_user.confirm_email = True
db.session.commit()



'''    <!-- Add additional info in Table -->
    <script type="text/javascript" charset="utf8" src="//code.jquery.com/jquery-3.5.1.js"></script>
    <script type="text/javascript" charset="utf8" src="//cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>

    <link rel="stylesheet" href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css">



        <!-- Add tabs -->
    <script type="text/javascript" charset="utf8" src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script type="text/javascript" charset="utf8" src="//cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>  
    <script type="text/javascript" charset="utf8" src="//cdn.datatables.net/1.12.1/js/dataTables.bootstrap.min.js"></script>  
    
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.12.1/css/dataTables.bootstrap.min.css">




'''