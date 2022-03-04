import pymysql

dbP2S = pymysql.connect(
    user='root',
    passwd='metrix',
    host='123.214.171.162',
    db='PAC',
    charset='utf8'
)

if __name__ == '__main__' :
    sql = 'SELECT psort, pcode_name FROM PA.pa_code where pcode_group=26;';
    
    db_conn = dbP2S.cursor();
    
    db_conn.execute(sql);
    rows = db_conn.fetchall()
    
    i=0;
    for col in rows: 
        i += 1
        print(col)
        if(i >= 100) :
            break;
    
    