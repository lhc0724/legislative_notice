from bs4 import BeautifulSoup
from noticeListParser import NoticeListParser

notices = NoticeListParser();

proc_maxPg = notices.getLastPage(0);
end_maxPg = notices.getLastPage(1);
