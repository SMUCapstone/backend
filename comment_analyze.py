import re 
# 딕셔너리에 저장하기 ( {시간:[댓글]} )
def find_timestamp(comments_list):
    # 밀집도 계산, 좌우 1초 잡아서 초당 평균 등장 횟수 계산
    def calc_mass(time_dic):
        average_freq = {}   # {시간:평균 등장 횟수}
        for stamp in time_dic:
            time = stamp.split(':')
            sec = time[-1]
            min = time[-2]
            leftmin = min
            rightmin = min
            if 1<=int(sec):
                left = str(int(sec)-1).zfill(2)
            elif sec=='00':
                left = '59'
                if int(min)>0:
                    leftmin = str(int(min)-1).zfill(2)
                else:
                    min = 0
                    left = '01'

            if int(sec)<59:
                right = str(int(sec)+1).zfill(2)
            elif sec=='59':
                right = '00'
                rightmin = str(int(min)+1).zfill(2)
            minus = leftmin+':'+left
            plus = rightmin+':'+right

            freq = (len(time_dic.get(minus, [])) + len(time_dic.get(stamp, [])) + len(time_dic.get(plus, [])))/3
            average_freq[stamp] = freq

            return average_freq

    time_dic = {}
    for comment in comments_list:
        time_stamps = re.findall(r'([0-5]?\d?:?[0-5]?\d:[0-5]\d)', comment)
        time_stamps = list(set(time_stamps))
        for stamp in time_stamps:
            hms=[x.zfill(2) for x in stamp.split(':')]
            alt_stamp = ":".join(hms)
            time_dic[alt_stamp] = time_dic.get(alt_stamp,[]) + [comment]
    
    result = []
    for x in dict(sorted(calc_mass(time_dic), key=lambda x:x[1], reverse=True)):
        result.append({str(x):{'freq':len(comments_list[x]), 'comment':comments_list[x]}})

        if len(result)>20:
            return result
    return result

        
    

# comment_list = ['1:34','1:35','1:3602:084:02 lol😂I heard hobi tho🥴🥴 lmao and many more 😂😂😂It was so cool to watch your blogg   now i wanna travel too😭😭😭', '0:00 0:00 0:00 내가 제일 좋아하는 부분','0:00']

# res = find_timestamp(comment_list)
# print(calc_mass(res))

#####################################################################################################################
# 워드클라우드 
def make_wordcloud(comment_list):
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    from collections import Counter
    from konlpy.tag import Okt
    from PIL import Image
    import numpy as np

    text = " ".join(comment_list)

    okt = Okt()
    nouns = okt.nouns(text) # 명사만 추출

    words = [n for n in nouns if len(n) > 1] # 단어의 길이가 1개인 것은 제외

    c = Counter(words)

    wc = WordCloud(font_path='malgun', width=400, height=400, scale=2.0, max_font_size=250)
    gen = wc.generate_from_frequencies(c)
    plt.figure()
    plt.imshow(gen)
    wc.to_file('법전_워드클라우드.png')

    return dict(c)

################################################################################################
import requests
from bs4 import BeautifulSoup

url = 'https://www.youtube.com/watch?v=fYyWM0i2lbk'

response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

title = soup.select('#related')