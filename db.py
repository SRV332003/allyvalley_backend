import psycopg2
import psycopg2.extras

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            database="allyvalley",
            user="postgres",
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.conn.commit()

    def query(self, query, params=None,assoc=True):
        self.cur.execute(query, params)
        self.conn.commit()
        try:
            return self.cur.fetchall()
        
        except:
            return None
    
    def reset(self,delete=False):
        if delete:
            self.query("Drop table if exists interests;")
            self.query("Drop table if exists messages;")
            self.query("Drop table if exists matches;")
            self.query("Drop table if exists users;")
           
            
            
        else:
            self.query("Truncate users;")
            self.query("Truncate messages;")
            self.query("Truncate matches;")
            self.query("Truncate interests;")
    

        
    def initialize(self):
        self.query("""Create table if not exists users (
                    id serial primary key,
                    email varchar(255) unique,
                    name varchar(255),
                    age varchar(255),
                    gender varchar(255),
                    languages varchar(255),
                    about varchar(255),
                    proffesion varchar(255),
                    phone varchar(255) unique,
                    lat float,
                    lon float,
                    status varchar(255) default 'true'
                );""")
        
        self.query("""Create table if not exists interests (
                    id serial primary key,
                    interest_name varchar(255) unique,
                    email varchar(255),
                    Foreign key (email) references users(email)
                );""")
        
        self.query("""Create table if not exists messages (
                    id serial primary key,
                    sender varchar(255),
                    receiver varchar(255),
                    message varchar(255),
                    timestamp timestamp,
                    Foreign key (sender) references users(email),
                    Foreign key (receiver) references users(email)
                );""")
        
        self.query("""Create table if not exists matches (
                    id serial primary key,
                    email1 varchar(255),
                    email2 varchar(255),
                    Foreign key (email1) references users(email),
                    Foreign key (email2) references users(email)
                );""")
        
        
    def __del__(self):
        self.conn.close()