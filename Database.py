# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 22:39:47 2022

@author: USER
"""

###### DB연동++++++++++++++++++++++++++++++++=====================================================
import pymysql
import pandas as pd
from pymysql.err import IntegrityError

#db connection (vpc 서버)
def get_connection():
    conn = pymysql.connect(host = '34.64.56.32', user = 'root', password = '2017', 
                       db="capstoneDB", charset = 'utf8mb4')
    return conn




########## 유튜버 테이블+++++++++++++++++++++++++====================================================
#유튜버 정보 입력 메소드
#유튜버 객체
class Youtuber():
    def __init__(self, id, channel, profile):
        self.id = id
        self.channel = channel
        self.profile = profile

#insert_youtuber_info 메소드
def insert_youtuber_info(u):
    '유튜버 정보 객체 받아서 sql 작성 후 정보 입력'
    sql = """insert into youtuber(id, channel, profile) values(%s, %s, %s)"""
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql,(u.id, u.channel, u.profile))
        conn.commit()

    except IntegrityError:
        pass

    except Exception as errmsg:
        print(errmsg)
        return 
    
    finally:
        conn.commit()
        curs.close()



########## 콘텐츠 테이블 +++++++++++++++++++++++++++===============================================
#콘텐츠 정보 입력 메소드
#콘텐츠 객체
class Content():
    #recognize를 제외한 인수 받기
    def __init__(self, id, url, video_name,thumbnail, hits, comment_num):
        self.id = id
        self.url = url
        self.video_name = video_name
        self.thumbnail = thumbnail
        self.hits = hits
        self.comment_num = comment_num
        
    @property
    def recognize(self):
    #recognize 속성 설정
    #대시를 언더바로 치환(별칭테이블 이름에 대시 사용 불가)
    #등호를 언더바로 치환
        rec = self.id + self.url[-3:]
        rec = rec.replace("-","_")
        rec = rec.replace("=","_")
        return rec

    @property
    def state(self):
    #댓글 정보 가져왔는지 상태확인
    # -1: before, 0: ing, 1: done
    # 기본값 -1
        return -1

#insert_content 메소드
def insert_content(c):
    '콘텐츠 정보 객체 받아서 sql 작성 후 정보 입력'
    sql = """insert into content(id, url, recognize, video_name,thumbnail, hits, comment_num, state) values(%s, %s, %s, %s, %s, %s, %s, %s)"""
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql,(c.id, c.url, c.recognize, c.video_name, c.thumbnail, c.hits, c.comment_num, c.state ))
        conn.commit()

    except IntegrityError:
        pass
    
    except Exception as errmsg:
        print(errmsg)
    
    finally:
        conn.commit()
        curs.close()
        
#콘텐츠의 식별정보(별칭)을 입력받음
#댓글 수집 요청 (state = 0)
def update_state_request(recognize):
    sql = "update content set state = 0 where recognize = '"+ recognize +"'"

    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        conn.commit()
        
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()
        
#콘텐츠의 식별정보(별칭)을 입력받음
#댓글 수집 작업중 (state = 1)
def update_state_ing(recognize):
    sql = "update content set state = 1 where recognize = '"+ recognize +"'"

    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        conn.commit()
        
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()

      
#콘텐츠의 식별정보(별칭)을 입력받음
#댓글 수집 작업 완료 (state = 100)
def update_state_done(recognize):
    sql = "update content set state = 100 where recognize = '"+ recognize +"'"

    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        conn.commit()
        
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()   


# show_another_3_video 메소드
def show_another_3_video(c):
    '분석화면에서 <채널명의 다른 콘텐츠>칸에 띄울 3개 영상 가져오는 메소드'
    
    # 현재 분석화면의 영상 제외하고 조회수 가장 많은 3가지 영상 가져옴
    sql = "select * from content where id = '" + c.id + "' and recognize <> '" + c.recognize +"' order by hits desc limit 3"
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        result = curs.fetchall()
        data = pd.DataFrame(result)
        return data
    
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        curs.close()        
        


####### 아카이브 테이블 ++++++++++++++++++++++++++++++++=============================================
#아카이브 자료 입력 메소드
#아카이브 객체
class Archive():
    def __init__(self, recognize, max, 
                 p1, p2, p3, p4, p5, p6, p7, p8, p9, p10,
                 n1, n2, n3, n4, n5, n6, n7, n8, n9, n10):
        
        self.recognize = recognize
        self.max = max
        
        #pos/neg 토큰 리스트 형태로 저장
        self.pos = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]
        self.neg = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10]


#insert_archive 메소드
def insert_archive(a):
    '아카이브 객체 받아서 sql 작성 후 정보 입력'
    sql = """insert into archive (recognize, max, pos1, pos2, pos3, pos4, pos5, pos6, pos7, pos8, pos9, pos10, 
            neg1, neg2, neg3, neg4, neg5, neg6, neg7, neg8, neg9, neg10) 
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        curs.execute(sql,(a.recognize, a.max, a.pos[0],a.pos[1],a.pos[2],a.pos[3],a.pos[4],a.pos[5],a.pos[6],a.pos[7],a.pos[8],a.pos[9], 
                      a.neg[0], a.neg[1], a.neg[2], a.neg[3], a.neg[4], a.neg[5], a.neg[6], a.neg[7], a.neg[8], a.neg[9]))
        conn.commit()

    except IntegrityError:
        pass
        
    except Exception as errmsg:
        print(errmsg)
    
    finally:
        conn.commit()
        curs.close()



# update_archive 메소드
# 정기적으로 크롤러 돌았을때 변경할 값이 있으면 호출해서 아카이브 정보 업데이트
# 해당 아카이브 삭제 후 재등록 하도록 구현
def update_archive(a):
    
    delete_archive = "delete from archive where recognize = '" + a.recognize +"'"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        # 기존 아카이브 레코드 삭제
        curs.execute(delete_archive)
        conn.commit()
        
        # insert_arhive 호출해서 아카이브 레코드 새로 생성
        insert_archive(a)

    except IntegrityError:
        pass

    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()


# get_archive_record 메소드
def get_archive_record(recognize):
    '아카이브 테이블에서 정보 가져오기'
    sql = "select * from archive where recognize = '" + recognize + "'"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        data = curs.fetchall()
    
        # 데이터 프레임 생성
        df = pd.DataFrame(data)
        #print(df.head())
    
        # 아카이브 객체 생성 후 정보 입력
        record = Archive(df.loc[0,'recognize'], df.loc[0,'max'], 
                     df.loc[0,'pos1'], df.loc[0,'pos2'], df.loc[0,'pos3'], df.loc[0,'pos4'], df.loc[0,'pos5'], 
                     df.loc[0,'pos6'], df.loc[0,'pos7'], df.loc[0,'pos8'], df.loc[0,'pos9'], df.loc[0,'pos10'],
                     df.loc[0,'neg1'], df.loc[0,'neg2'], df.loc[0,'neg3'], df.loc[0,'neg4'], df.loc[0,'neg5'],
                     df.loc[0,'neg6'], df.loc[0,'neg7'], df.loc[0,'neg8'], df.loc[0,'neg9'], df.loc[0,'neg10'])
    
        # record 반환
        return record
    
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()



########## 별칭 테이블 ++++++++++++++++++++++++++++++++++============================================
# create_raw_comment_table 메소드
def create_raw_comment_table(recognize):
    'content테이블에서 별칭 이름 받아서 해당 영상의 raw comment 테이블 생성'
    
    sql = "create table "+ recognize + "(comment varchar(10000), like_num int, response int);"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        conn.commit()

    except IntegrityError:
        pass

    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()


# raw 코멘트 객체
# response 속성 초기값 1
class Rcomment():
    def __init__ (self, comment, like_num):
        self.comment = comment
        self.like_num = like_num
        
    @property
    def response(self):
        return 1


# insert_raw_comment 메소드
def insert_raw_comment(recognize, r):
    '별칭(테이블명), r코멘트 객체 입력 받아서 sql 작성 후 정보 입력'
    
    # response 열 초기값: null 추후 update_response()로 정보 update
    sql = "insert into " + recognize + "(comment, like_num, response) values(%s, %s, %s)"
    
    # insert전 unique 체크
    check = "select * from " + recognize + " where comment = '" + r.comment + "'"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        # unique 결과 값이 0(동일한 코멘트 없음)이면 R코멘트 insert
        unique = curs.execute(check)
        if(unique==0):
            curs.execute(sql,(r.comment, r.like_num, r.response))
            conn.commit()

    except IntegrityError:
        pass

    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()


# 별칭 테이블 response열 업데이트 메소드
# response 열 기본값은 1, 부정적 반응일때만 update_response 호출하여 0로 업데이트
# 긍정반응보다 부정반응이 더 적을 것이라고 예상됨, 오버헤드 최소화
# recognize(테이블 이름), r객체 입력받음
def update_response(recognize, r):
    '부정반응일때만 response열 0로 업데이트, comment = r.comment 완전일치로 찾아들어감'
    sql = "update " + recognize + " set response = 0 where comment = '" + r.comment +"'"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        # 키 없이 업데이트 수행할 때 발생하는 오류 방지하기 위해 safe모드 해제
        safe_unlock = "set sql_safe_updates=0"
        curs.execute(safe_unlock)
        
        curs.execute(sql)
        conn.commit()
    
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()




####### 운영 search(검색어) +++++++++++++++++++++============================================================
#search메소드
def search(key):
    '유튜버&콘텐츠 테이블 조인해서 검색하기'
    #특이사항: 유튜브 테이블에 정보 있더라도 콘텐츠 테이블에 항목이 없으면 결과 없음.
    #콘텐츠 등록 안하더라도 검색하고 싶으면 union으로 변경
    #select * from youtuber y left join content c on y.id=c.id union select * from youtuber y right join content c on y.id=c.id;
    sql = "select * from youtuber natural join content where youtuber.id like '%" + key + "%' or " +"url like '%" + key + "%' or " + "video_name like '%" + key + "%' or " + "channel like '%" + key +"%'"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        #sql 실행하여 몇행 반환하는지 num에 저장, result에 결과값 저장
        num = curs.execute(sql)
        result = curs.fetchall()
        
        #결과값 있으면 데이터 프레임과 행 수 return, 없으면 0 return
        if(result):
            result = pd.DataFrame(result)
            return result, num
        else:
            return 0, 0
    
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()

####### 운영 delYoutuber(채널id) +++++++++++++++++++++============================================================
def delYoutuber(id):
    # '유튜버 등록 삭제하기'
    sql = f"delete from youtuber where id='{id}'"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        result = curs.fetchall()
   
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()

def getYoutuber():
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from youtuber"
    curs.execute(sql)
    result = curs.fetchall()
    data = pd.DataFrame(result)
    return data

def getContent(channelId):
    conn = get_connection()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = f"select * from content where id='{channelId}'"
    curs.execute(sql)
    result = curs.fetchall()
    data = pd.DataFrame(result)
    return data

def update_last_page(recognize, page):
    'page token 업데이트'
    sql = "update content set last_page = '" + page + "' where recognize = '" + recognize +"'"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        # 키 없이 업데이트 수행할 때 발생하는 오류 방지하기 위해 safe모드 해제
        safe_unlock = "set sql_safe_updates=0"
        curs.execute(safe_unlock)
        
        curs.execute(sql)
        conn.commit()
        
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()


def search_request_state():
    'content테이블에서 수행중(state = 0)인 row 1개 선택'
    
    sql = "select recognize from content where state = 0 Limit 1"
    
    try:
        conn = get_connection()
        curs = conn.cursor(pymysql.cursors.DictCursor)
        
        curs.execute(sql)
        recognize = curs.fetchall()
        
        # 검색 결과 있음 -> recognize 리턴
        if(recognize):
            return recognize
        
        # 검색 결과 없음 -> -1 리턴
        else:
            return -1
        
    except Exception as errmsg:
        print(errmsg)
        
    finally:
        conn.commit()
        curs.close()