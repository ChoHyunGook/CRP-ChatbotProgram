from bs4 import BeautifulSoup
import urllib.request



import numpy as np
import pandas as pd
from icecream import ic
import math

from matplotlib import rc, font_manager, pyplot as plt
rc('font', family=font_manager.FontProperties(fname='C:/Windows/Fonts/malgunsl.ttf').get_name())

import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False

from context.domains import Reader, File


class Solution(Reader):
    def __init__(self,k=0.5):
        self.file=File()
        self.file.context='./data/'
        self.movie_comments=pd.DataFrame
        # 나이브베이즈 설정값
        self.k = k
        self.word_probs = []


    def hook(self):
        def print_menu():
            print('0. Exit')
            print('1. movie_reviews.txt 파일 생성')
            print('2. movie_reviews.txt 파일 csv로 변경')
            print('3. 전처리')
            print('4. 영화 댓글이 긍정인지 부정인지 ratio 값으로 판단하시오.\n'
                  '너무 좋아요. 내 인생의 최고의 영화\n'
                  '이렇게 졸린 영화는 처음이야')
            return input('메뉴 선택 \n')

        while 1:
            menu = print_menu()
            if menu == '0':
                break
            elif menu == '1':
                self.crawling()
            elif menu == '2':
                self.streotype()
            elif menu == '3':
                self.preprocess()


    def crawling(self):#txt로 크롤링
        file=self.file
        file.context='./save/'
        file.fname='movie_reviews.txt'
        path=self.new_file(file)
        f = open(path, 'w', encoding='UTF-8')
        for no in range(1, 501):
            url = 'https://movie.naver.com/movie/point/af/list.naver?&page=%d' % no
            html = urllib.request.urlopen(url)
            soup = BeautifulSoup(html, 'html.parser')

            reviews = soup.select('tbody > tr > td.title')
            for rev in reviews:
                rev_lst = []
                title = rev.select_one('a.movie').text.strip()
                score = rev.select_one('div.list_netizen_score > em').text.strip()
                comment = rev.select_one('br').next_sibling.strip()

                # -- 긍정/부정 리뷰 레이블 설정
                if int(score) >= 8:
                    label = 1  # -- 긍정 리뷰 (8~10점)
                elif int(score) <= 4:
                    label = 0  # -- 부정 리뷰 (0~4점)
                else:
                    label = 2

                f.write(f'{title}\t{score}\t{comment}\t{label}\n')
        f.close()

    def save_csv(self):
        data = pd.read_csv('./save/movie_reviews.txt', delimiter='\t',
                           names=['title', 'score', 'comment', 'label'])  # -- 본인 환경에 맞게 설치 경로 변경할 것
        new_csv_file = data.to_csv(r'./save/movie_reviews.csv')#txt파일 csv로 변경 정형화
        return new_csv_file

    def streotype(self):
        file = self.file
        file.context='./save/'
        file.fname = 'movie_reviews.txt'
        path=self.new_file(file)
        self.movie_comments = pd.read_csv(path, delimiter='\t',
                           names=['title', 'score', 'comment', 'label'])  # -- 본인 환경에 맞게 설치 경로 변경할 것


    def preprocess(self):#전처리=>읽기
        file = self.file
        file.context = './save/'
        file.fname = 'movie_reviews'
        df = self.csv(file)
        df = df.dropna()  # 코멘트 없는 리뷰데이터(NaN) 제거
        df = df.drop_duplicates(['comment'])  # 중복 리뷰 제거
        #self.reviews_info(df) #=> 분석
        top10 = self.top10_movies(df)
        avg_score=self.get_avg_score(top10)
        self.visualization(top10, avg_score)



    def reviews_info(self,df):
         movie_lst = df.title.unique()  # 영화 리스트 확인
         ic('전체 영화 편수 =', len(movie_lst))
         ic(movie_lst[:10])
         cnt_movie = df.title.value_counts()  # 각 영화 리뷰 수 계산
         ic(cnt_movie[:20])
         info_movie = df.groupby('title')['score'].describe()
         info_movie.sort_values(by=['count'], axis=0, ascending=False)  # 각 영화 평점분석
         #ic((lambda a,b: df.groupby(a)[b].describe())('title','score').sort_values(by=['count'], axis=0, ascending=False))
         df.label.value_counts()  # 긍정,부정 리뷰 수

    def top10_movies(self,df):
        top10 = df.title.value_counts().sort_values(ascending=False)[:10]
        top10_title = top10.index.tolist()
        return df[df['title'].isin(top10_title)]

    def get_avg_score(self, top10):
        movie_title = top10.title.unique().tolist()  # -- 영화 제목 추출
        avg_score = {}  # -- {제목 : 평균} 저장
        for t in movie_title:
            avg = top10[top10['title'] == t]['score'].mean()
            avg_score[t] = avg
        return avg_score

    def visualization(self, top10, avg_score):
        plt.figure(figsize=(10, 5))
        plt.title('영화 평균 평점 (top 10: 리뷰 수)\n', fontsize=17)
        plt.xlabel('영화 제목')
        plt.ylabel('평균 평점')
        plt.xticks(rotation=20)

        for x, y in avg_score.items():
            color = np.array_str(np.where(y == max(avg_score.values()), 'orange', 'lightgrey'))
            plt.bar(x, y, color=color)
            plt.text(x, y, '%.2f' % y,
                     horizontalalignment='center',
                     verticalalignment='bottom')

        #plt.show()
        self.rating_distribution(top10, avg_score)
        self.circle_chart(top10, avg_score)

    def rating_distribution(self,top10,avg_score):
        fig, axs = plt.subplots(5, 2, figsize=(15, 25))
        axs = axs.flatten()

        for title, avg, ax in zip(avg_score.keys(), avg_score.values(), axs):
            num_reviews = len(top10[top10['title'] == title])
            x = np.arange(num_reviews)
            y = top10[top10['title'] == title]['score']
            ax.set_title('\n%s (%d명)' % (title, num_reviews), fontsize=15)
            ax.set_ylim(0, 10.5, 2)
            ax.plot(x, y, 'o')
            ax.axhline(avg, color='red', linestyle='--')  # -- 평균 점선 나타내기

        plt.show()

    def circle_chart(self, top10, avg_score):
        fig, axs = plt.subplots(5, 2, figsize=(15, 25))
        axs = axs.flatten()
        colors = ['pink', 'gold', 'whitesmoke']
        labels = ['1 (8~10점)', '0 (1~4점)', '2 (5~7점)']

        for title, ax in zip(avg_score.keys(), axs):
            num_reviews = len(top10[top10['title'] == title])
            values = top10[top10['title'] == title]['label'].value_counts()
            ax.set_title('\n%s (%d명)' % (title, num_reviews), fontsize=15)
            ax.pie(values,
                   autopct='%1.1f%%',
                   colors=colors,
                   shadow=True,
                   startangle=90)
            ax.axis('equal')
        plt.show()

    def tokenization(self):#토큰화=>
        pass

    def embedding(self):#임베딩=>벡터화
        pass



    def naiveBayesClassifier(self,doc):
        path =''
        self.load_corpus()
        training_set=None
        self.count_words(training_set)
        counts=0
        total_class0=0
        total_class1=0
        k=self.k
        word_probs =0
        trainfile_path=''
        self.word_probabilities(counts,total_class0,total_class1,k)
        self.class0_probabilities(word_probs,doc)
        self.train(trainfile_path)
        self.classify(doc)

    def load_corpus(self):
        file = self.file
        file.context = './save/'
        file.fname = 'movie_reviews'
        corpus = self.csv(file)
        corpus = pd.read_table()
        return corpus

    def count_words(self, training_set):
        counts = 0
        return counts

    def isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def word_probabilities(self, counts, total_class0, total_class1, k):
        # 단어의 빈도수를 [단어, p(wl긍정), p(w|부정)] 형태로 변환
        return []

    def class0_probabilities(self, word_probs, doc):
        return None

    def train(self, trainfile_path):
        pass

    def classify(self, doc):
        return self.class0_probabilities(self.word_probs, doc)

if __name__ == '__main__':
    Solution().hook()


