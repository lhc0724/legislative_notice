from bs4 import BeautifulSoup
import crawler
import db

def main() :
    notices = crawler.NoticeListParser();
    conf = db.db_config();
    
    proc_maxPg = notices.getLastPage(0);
    end_maxPg = notices.getLastPage(1);
    
    if(proc_maxPg == 0 or end_maxPg == 0) :
        return ;
    
    for i in range(1, proc_maxPg+1) :
        conf.insert_value(notices.getListValue(i));
    
    return ;

if __name__ == '__main__' :
    main();