from bs4 import BeautifulSoup
from noticeListParser import NoticeListParser

import pymysql

dbP2S = pymysql.connect(
    user='root',
    passwd='metrix',
    host='123.214.171.162',
    db='PAC',
    charset='utf8'
)

def main() :
    notices = NoticeListParser();

    proc_maxPg = notices.getLastPage(0);
    end_maxPg = notices.getLastPage(1);
    
    if(proc_maxPg == 0 or end_maxPg == 0) :
        return ;

    for i in range(1, proc_maxPg) :
        listVals = notices.getListValue(i)
        listVals['notice_status'] = 1
        print(listVals);
    
    return ;

if __name__ == '__main__' :
    main();