###### DB연동++++++++++++++++++++++++++++++++
import pymysql
import pandas as pd

#db connection (aws mysql 서버)
conn = pymysql.connect(host = 'capstone.cyh0mfc8nj8f.ap-northeast-2.rds.amazonaws.com', user = 'admin', password = 'capstone22', 
                       db="capstone", charset = 'utf8')
curs = conn.cursor(pymysql.cursors.DictCursor)


########## 유튜버 테이블+++++++++++++++++++++++++
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
    curs.execute(sql,(u.id, u.channel, u.profile))
    conn.commit()


########## 콘텐츠 테이블 +++++++++++++++++++++++++++
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
        rec = self.id + self.url[-3:]
        rec = rec.replace("-","_")
        return rec


#insert_content 메소드
def insert_content(c):
    '콘텐츠 정보 객체 받아서 sql 작성 후 정보 입력'
    sql = """insert into content(id, url, recognize, video_name,thumbnail, hits, comment_num) values(%s, %s, %s, %s, %s, %s, %s)"""
    curs.execute(sql,(c.id, c.url, c.recognize, c.video_name, c.thumbnail, c.hits, c.comment_num ))
    conn.commit()



####### 아카이브 테이블 ++++++++++++++++++++++++++++++++
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
    
    curs.execute(sql,(a.recognize, a.max, a.pos[0],a.pos[1],a.pos[2],a.pos[3],a.pos[4],a.pos[5],a.pos[6],a.pos[7],a.pos[8],a.pos[9], 
                      a.neg[0], a.neg[1], a.neg[2], a.neg[3], a.neg[4], a.neg[5], a.neg[6], a.neg[7], a.neg[8], a.neg[9]))
    conn.commit()



# get_archive_record 메소드
def get_archive_record(recognize):
    '아카이브 테이블에서 정보 가져오기'
    sql = "select * from archive where recognize = '" + recognize + "'"
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




########## 별칭 테이블 ++++++++++++++++++++++++++++++++++
# create_raw_comment_table 메소드
def create_raw_comment_table(recognize):
    'content테이블에서 별칭 이름 받아서 해당 영상의 raw comment 테이블 생성'
    
    sql = "create table "+ recognize + "(comment varchar(10000), like_num varchar(5), response int);"
    curs.execute(sql)
    conn.commit()


#별칭 테이블 response열 업데이트 ????????????????(구현 미룸... where claue 모호성)????????????????????????




####### 운영 search(검색어) +++++++++++++++++++++
#search메소드
def search(key):
    '유튜버&콘텐츠 테이블 조인해서 검색하기'
    #특이사항: 유튜브 테이블에 정보 있더라도 콘텐츠 테이블에 항목이 없으면 결과 없음.
    #콘텐츠 등록 안하더라도 검색하고 싶으면 union으로 변경
    #select * from youtuber y left join content c on y.id=c.id union select * from youtuber y right join content c on y.id=c.id;
    sql = "select * from youtuber natural join content where youtuber.id like '%" + key + "%' or " +"url like '%" + key + "%' or " + "video_name like '%" + key + "%' or " + "channel like '%" + key +"%'"
    
    #sql 실행하여 몇행 반환하는지 num에 저장, result에 결과값 저장
    num = curs.execute(sql)
    result = curs.fetchall()
   
    #결과값 있으면 데이터 프레임과 행수 return, 없으면 0 return
    if(result):
        result = pd.DataFrame(result)
        return result, num
    else:
        return 0, 0


# ###### 실행예시 ++++++++++++++++++++++++++++++
# 유튜브 테이블 모든 정보 출력
sql = "select * from youtuber"
curs.execute(sql)
result = curs.fetchall()
data = pd.DataFrame(result)
data

# 콘텐츠 테이블 모든 정보 출력
sql = "select * from content"
curs.execute(sql)
result = curs.fetchall()
data = pd.DataFrame(result)
print(data)


# 아카이브 테이블 모든 정보 출력
sql = "select * from archive"
curs.execute(sql)
result = curs.fetchall()
data = pd.DataFrame(result)
data


# search 실행예시
data, num = search('백현')
print('총 검색결과: '+ str(num) +'건\n')
print(data)

# get_archive_record 실행 예시
record = get_archive_record('baekhyunGP0')
print(record.recognize)
print(record.max)
print(record.pos[0:10])