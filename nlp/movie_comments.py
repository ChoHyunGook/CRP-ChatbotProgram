from bs4 import BeautifulSoup
import urllib.request

import pandas as pd

from context.domains import Reader, File


class Solution(Reader):
    def __init__(self):
        self.file=File()
        self.file.context='./data/'
        self.movie_comments=pd.DataFrame

    def hook(self):
        def print_menu():
            print('0. Exit')
            print('1. movie_reviews.txt 파일 생성')
            print('2. movie_reviews.txt 파일 csv로 변경')
            print('3. 전처리')
            print('4. 시각화')
            return input('메뉴 선택 \n')

        while 1:
            menu = print_menu()
            if menu == '0':
                break
            elif menu == '1':
                self.crawling()
            elif menu == '2':
                self.change()


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
        file.fname = 'movie_reviews'
        df_data = self.csv(file)
        df_reviews = df_data.dropna()  # 코멘트 없는 리뷰데이터(NaN) 제거
        df_reviews = df_reviews.drop_duplicates(['comment'])  # 중복 리뷰 제거
        movie_lst = df_reviews.title.unique()  # 영화 리스트 확인
        cnt_movie = df_reviews.title.value_counts()  # 각 영화 리뷰 수 계산
        info_movie = df_reviews.groupby('title')['score'].describe()
        info_movie.sort_values(by=['count'], axis=0, ascending=False)  # 각 영화 평점분석
        df_reviews.label.value_counts()  # 긍정,부정 리뷰 수

    def tokenization(self):#토큰화=>
        pass

    def embedding(self):#임베딩=>벡터화
        pass

if __name__ == '__main__':
    Solution().hook()


