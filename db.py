import psycopg2

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            database="allyvalley",
            user="postgres",
        )
        self.cur = self.conn.cursor()
        self.conn.commit()

    def query(self, query, params=None):
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur.fetchall()
    
    def reset(self):
        self.query("Truncate users;")
        self.query("Truncate messages;")
        self.query("Truncate matches;")
        
    def initialize(self):
        self.query("""Create table if not exists users (
                    id serial primary key,
                    email varchar(255) unique,
                    age int,
                    gender varchar(255),
                    languages varchar(255),
                    about varchar(255),
                    proffesion varchar(255),
                    phone varchar(255) unique,
                    interests varchar(255) 
            );""")
        
        self.query("""Create table if not exists interests (
                    id serial primary key,
                    user_id int,
                    Lower(interest_name) varchar(255) unique,
                    Foreign key (user_id) references users(id)
            );""") 
        self.query("""Create table if not exists messages (
                    id serial primary key,
                    sender int,
                    receiver int,
                    message varchar(255),
                    timestamp timestamp,
                    Foreign key (sender) references users(id),
                    Foreign key (receiver) references users(id)
            );""")
        self.query("""Create table if not exists matches (
                    id serial primary key,
                    user1 int,
                    user2 int,
                    Foreign key (user1) references users(id),
                    Foreign key (user2) references users(id)
            );""")

    def __del__(self):
        self.conn.close()

