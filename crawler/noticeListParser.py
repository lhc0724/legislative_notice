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
    
    # 법안번호의 최대길이
    __billNoLen = 7
    
    def __init__(self) -> None:
        #http urls (main List)
        self.base_url = 'https://pal.assembly.go.kr'          #국회 입법예고 홈페이지 URL
        self.proc_url = self.base_url + "/law/listView.do"    #진행중인 입법예고 리스트 URL
        self.end_url = self.base_url + "/law/endListView.do"  #종료된 입법예고 리스트 URL
        
        #http urls (suggestion List)
        self.sugg_url = '/suggestion'
        self.procSugg_url = self.base_url + self.sugg_url + '/listView.do'
        self.endSugg_url = self.base_url + self.sugg_url + '/listEndView.do'
        
        #http url query string params
        self.qs_page = 'pageNo'                     
        self.qs_isClosed = 'closedCondition'
        self.qs_age = 'age'
        self.qs_suggId = 'lgsltpaId'
        
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
    
    def getListValue(self, pgNum=1, isClosed=0, age=__maxAge) -> list:
        if(isClosed == 0 ) :
            html = self.getProceedNotice(pgNum=pgNum);
        elif(isClosed == 1) :
            html = self.getEndNotice(pgNum=pgNum);
        
        if(html == 0) :
            return [];
        
        #table td 하위 태그 중 class 값이 left 혹은 center인 값 검색
        #tblAttrs = html.find_all('tr');
        tblAttrs = html.find_all('td', {'class': re.compile('left|center')});
        
        toStrList = []
        for item in tblAttrs :
            toStrList.append(str(item));
        
        #bill_id parsing
        billId = []
        billNum = []
        committee = []
        commentNum = []
        for item in toStrList :
            tmp_id = re.findall(r'getRead\(\'[\w]*',item);
            tmpNum = re.findall(r'\d+', item);
            
            #html tag안의 title값 검색
            tmpTitle = re.findall(r'title\=\"[\w+]*', item);    
            
            #_getRead('[bill_id]') 형태의 값을 찾기 때문에, findall에서 빈배열 반환 이경우 len(list)으로 걸러줌..
            if(len(tmp_id)) :
                billId.append(re.findall(r'(\w+)\'?', tmp_id[0])[1]);
            
            #소속 위원회 필터링
            if(len(tmpTitle)) :
                tmp = (re.findall(r'\"(\w+위원회)', tmpTitle[0]));
                if(len(tmp)) :
                    committee.append(tmp[0]);
            
            #태그 한줄당 숫자값을 가져올 경우 법안번호와 의견수는 숫자 배열 길이가 1, 그 외는 0 이거나 잡다한 값이 아주 많음
            if(len(tmpNum) == 1) :
                number = tmpNum[0];
                #법안 번호 조건이 아닐경우 의견수가 됨.
                if(len(number)==self.__billNoLen and number[0:2] == str(age)) :
                    billNum.append(number);
                else :
                    commentNum.append(number);
        
        resList = []
        for i in range(0,len(billId)) :
            try :
                resList.append(
                {   
                    'bill_id': billId[i],
                    'bill_no': billNum[i], 
                    'committee': committee[i],
                    'status': not(isClosed),
                    'cmnt_cnt': commentNum[i]
                });
            # list length가 달라 크롤링이 제대로 안된 경우.
            except IndexError as err: 
                print(err);
        return resList
    
    
    def getOpinionCnt(self, pgNum=1, age=__maxAge, bill_id='', isClosed=False):
        
        #현재 법안의 찬/반 카운트 변수
        agreeCnt = 0;
        oppositCnt = 0;
        
        #http post request params
        params = { self.qs_suggId: bill_id, self.qs_age: age, self.qs_page: pgNum};
        
        if(isClosed) :
            res = requests.post(self.endSugg_url, params=params);  
        else :
            res = requests.post(self.procSugg_url, params=params);  
        
        if(res.status_code == 200) :
            soup = BeautifulSoup(res.content, 'html.parser');
        else:
            print(res.status_code);
            return 0;
        
        
        #현재 게시판의 의견 테이블 마지막 페이지 크롤링
        pagesTag = soup.find_all("a", {'href' : re.compile('javascript-*')});
        pgVals = []
        
        # 가져온 태그들 내에서 탐색
        for item in pagesTag : 
            tmp = str(item) #객체를 string으로 변환
            #정규식으로 괄호 안의 숫자만 가져옴
            pgVals.append([int(s) for s in re.findall(r'\(([^)]+)', tmp)][0]);
            
        maxPg = max(pgVals);    #마지막 페이지값

        tblAttrs = soup.find_all('td', {'class': re.compile('left')});
        #print(tblAttrs);
        
        htmlStrList = []
        for item in tblAttrs:
            htmlStrList.append(str(item));
           # print(f'{item}\r\n')
        
        return soup;
    
        
#module test
if __name__ == '__main__' :
    test = NoticeListParser();
    
    result = test.getOpinionCnt(pgNum=1, isClosed=True, bill_id='PRC_Y2E2H0X2S2J4H1K4A2Z0E4A6M9H1U1');
    
