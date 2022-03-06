import pymysql
from dotenv import load_dotenv;
import os

class db_config:
    def __init__(self) -> None: 
        load_dotenv()
        self.config = {
            'user':os.environ.get('DB_USER'),
            'db':os.environ.get('DB_NAME'),
            'port':os.environ.get('DB_PORT'),
            'passwd':os.environ.get('DB_PW'),
            'host':os.environ.get('DB_HOST'),
            'charset':'utf8'
        }

    def connect_db(self):
        conn = pymysql.connect(
            user=self.config['user'],
            db=self.config['db'],
            port=int(self.config['port']),
            passwd=self.config['passwd'],
            host=self.config['host'],
            charset=self.config['charset']
        )

        return conn;
        # if(isDict):
        #     cursor = conn.cursor(pymysql.cursors.DictCursor);
        # else :
        #     cursor = conn.cursor();
        # return cursor;

    #datas attr type (list in dict): [{'key' : 'data'} ... ] 
    def insert_list(self, datas) -> bool:
        conn = self.connect_db();
        cursor = conn.cursor(pymysql.cursors.DictCursor);
        
        isSuccess = True
        
        if(len(datas)) :
            sqlcmd = (
                f"insert into `leg_notice_list` ({', '.join(datas[0].keys())}) "
                f"values (%({')s, %('.join(datas[0].keys())})s) "
                f"on duplicate key update "
                f"cmnt_cnt = values(cmnt_cnt), status = values(status)"
            )
        
        try :    
            cursor.executemany(sqlcmd, datas);
            conn.commit();
        except:
            isSuccess = False;
        finally:
            conn.close();
            
        return isSuccess;

    def insert_opinionCnt(self, datas) -> bool :
        # agreeCnt = 0;
        # oppositCnt = 0;
        
        return True;

if __name__ == '__main__' :
    
    config = db_config();
    
    sql = 'select * from users'
    conn = config.connect_db();
    
    conn.execute(sql)
    
    rows = conn.fetchall();
    print(rows);