from xml.dom.minidom import TypeInfo
import requests
from bs4 import BeautifulSoup
import re

"""
ASMetrix 법안 관심도 컨텐츠를 위한 국회 입법예고 홈페이지 데이터 수집기

noticeListParser: 
    홈페이지에 등록되어있는 입법예고 리스트들을 가져와 1차적으로 데이터 가공
    리스트 목록과 법안별 의견수만 가져옴.
"""

class NoticeListParser:
    # 검색 가능한 국회 범위(19~21대)
    __maxAge = 21
    __minAge = 19
    
    def __init__(self) -> None:
        #http urls
        self.base_url = 'https://pal.assembly.go.kr'          #국회 입법예고 홈페이지 URL
        self.proc_url = self.base_url + "/law/listView.do"    #진행중인 입법예고 리스트 URL
        self.end_url = self.base_url + "/law/endListView.do"  #종료된 입법예고 리스트 URL
        #http url query string params
        self.qs_page = 'pageNo'                     
        self.qs_isClosed = 'closedCondition'
        self.qs_age = 'age'
        
        
    #현재 진행중인 입법예고 리스트 가져오기, default page=1
    def getProceedNotice(self, pgNum=1):
        isClosed = 0;
        params = {self.qs_page: pgNum, self.qs_isClosed: isClosed};
        res = requests.post(self.proc_url, params=params);  
        
        if(res.status_code == 200) :
            soup = BeautifulSoup(res.content, 'html.parser');
        else:
            print(res.status_code);
            return 0;
        
        return soup;
    
    #입법예고가 끝난 리스트 가져오기, default page=1, default age=21 (몇대 국회인지 나타내는 값)
    def getEndNotice(self, pgNum=1, age=__maxAge):
        #valid age range: 19~21
        if(age < self.__minAge or age > self.__maxAge):
            return 0
        
        isClosed = 1;
        params = {self.qs_page: pgNum, self.qs_isClosed: isClosed, self.qs_age: age};
        
        res = requests.post(self.end_url, params=params);  
        
        if(res.status_code == 200) :
            soup = BeautifulSoup(res.content, 'html.parser');
        else:
            print(res.status_code);
            return 0;
        
        return soup;
    
    #진행/종료 입법예고 마지막 페이지 값 파싱함수
    def getLastPage(self, isClosed=0):
        if(isClosed == 0 ) :
            html = self.getProceedNotice();
        elif(isClosed == 1) :
            html = self.getEndNotice();
        
        if(html == 0) :
            return 0;
        
        
        """
        html.find_all 결과 예시: 
            <a href="javascript:_getList(1)"><span class="page_n">1</span></a> 
            ...
            <a href="javascript:_getList(1373)"><img alt="마지막 페이지로 이동" src="/img/page_next1.gif" boarder="0" align="absmiddle"></a>
        """
        pagesTag = html.find_all("a", {'href' : re.compile('javascript-*')});
        
        pageVal = []
        
        # 가져온 태그들 내에서 탐색
        for item in pagesTag : 
            tmp = str(item) #객체를 string으로 변환
            #정규식으로 괄호 안의 숫자만 가져옴
            pageVal.append([int(s) for s in re.findall(r'\(([^)]+)', tmp)][0]);
        
        return max(pageVal);
    
    def getListValue(self, pgNum=1, isClosed=0):
        if(isClosed == 0 ) :
            html = self.getProceedNotice(pgNum=pgNum);
        elif(isClosed == 1) :
            html = self.getEndNotice(pgNum=pgNum);
        
        if(html == 0) :
            return 0;
        
        test = html.find_all('tr');
        
        result = []
        for item in test :
            result.append(str(item));
            print(str(item))   ;
            print('###############')
        #print(result);
        
        test2 = []
        for item in result :
            tmp = re.findall('getRead\(\'[\w]*',item);
            
            if(len(tmp)) :
                test2.append(tmp[0]);
            
        print(test2)
        
        # billInfo = html.find_all('td', {'class': re.compile('left|center')});
        
        # tableList = []
        # for item in billInfo: 
        #     tmp = str(item);
        #     itemTxt = str(item.text);
        #     tableList.append(tmp);
            
        # for i in tableList:
        #     print(i);
        
        return ;

#module test
if __name__ == '__main__' :
    test = NoticeListParser();
    
    test.getListValue(pgNum=2);