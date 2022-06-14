

from context.domains import Reader, File

import pandas as pd
import numpy as np

import platform
import matplotlib.pyplot as plt


class Solution(Reader):

    def __init__(self):
        self.file = File()
        self.file.context = './data/'

    def hook(self):
        def print_menu():
            print('0. Exit')
            print('1. 인구 데이터 확보하고 정리하기')
            print('2. 인구 소멸 위기 지역 계산하고 데이터 정리하기')
            print('3. 지도 시각화를 위해 지역별 고유 ID 만들기')
            return input('메뉴 선택 \n')

        while 1:
            menu = print_menu()
            if menu == '0':
                break
            elif menu == '1':
                self.one()
            elif menu == '2':
                self.two()
            elif menu == '3':
                self.three()


    def one(self):
        population = pd.read_excel('./data/05. population_raw_data.xlsx', header=1)
        population.fillna(method='pad', inplace=True)

        population.rename(columns={'행정구역(동읍면)별(1)': '광역시도',
                                   '행정구역(동읍면)별(2)': '시도',
                                   '계': '인구수'}, inplace=True)

        population = population[(population['시도'] != '소계')]
        population.is_copy = False

        population.rename(columns={'항목': '구분'}, inplace=True)

        population.loc[population['구분'] == '총인구수 (명)', '구분'] = '합계'
        population.loc[population['구분'] == '남자인구수 (명)', '구분'] = '남자'
        population.loc[population['구분'] == '여자인구수 (명)', '구분'] = '여자'
        population['20-39세'] = population['20 - 24세'] + population['25 - 29세'] + \
                               population['30 - 34세'] + population['35 - 39세']

        population['65세이상'] = population['65 - 69세'] + population['70 - 74세'] + \
                              population['75 - 79세'] + population['80 - 84세'] + \
                              population['85 - 89세'] + population['90 - 94세'] + \
                              population['95 - 99세'] + population['100+']

        population.head(10)

        print(population)
        return population

    def two(self):
        population=self.first()
        pop = pd.pivot_table(population,
                             index=['광역시도', '시도'],
                             columns=['구분'],
                             values=['인구수', '20-39세', '65세이상'])

        pop['소멸비율'] = pop['20-39세', '여자'] / (pop['65세이상', '합계'] / 2)
        pop.head()
        pop['소멸위기지역'] = pop['소멸비율'] < 1.0
        pop.head()
        pop[pop['소멸위기지역'] == True].index.get_level_values(1)
        pop.reset_index(inplace=True)
        pop.head()
        tmp_coloumns = [pop.columns.get_level_values(0)[n] + \
                        pop.columns.get_level_values(1)[n]
                        for n in range(0, len(pop.columns.get_level_values(0)))]

        pop.columns = tmp_coloumns
        pop.head()
        pop.info()
        pop['시도'].unique()
        si_name = [None] * len(pop)

        tmp_gu_dict = {'수원': ['장안구', '권선구', '팔달구', '영통구'],
                       '성남': ['수정구', '중원구', '분당구'],
                       '안양': ['만안구', '동안구'],
                       '안산': ['상록구', '단원구'],
                       '고양': ['덕양구', '일산동구', '일산서구'],
                       '용인': ['처인구', '기흥구', '수지구'],
                       '청주': ['상당구', '서원구', '흥덕구', '청원구'],
                       '천안': ['동남구', '서북구'],
                       '전주': ['완산구', '덕진구'],
                       '포항': ['남구', '북구'],
                       '창원': ['의창구', '성산구', '진해구', '마산합포구', '마산회원구'],
                       '부천': ['오정구', '원미구', '소사구']}

        for n in pop.index:
            if pop['광역시도'][n][-3:] not in ['광역시', '특별시', '자치시']:
                if pop['시도'][n][:-1] == '고성' and pop['광역시도'][n] == '강원도':
                    si_name[n] = '고성(강원)'
                elif pop['시도'][n][:-1] == '고성' and pop['광역시도'][n] == '경상남도':
                    si_name[n] = '고성(경남)'
                else:
                    si_name[n] = pop['시도'][n][:-1]

                for keys, values in tmp_gu_dict.items():
                    if pop['시도'][n] in values:
                        if len(pop['시도'][n]) == 2:
                            si_name[n] = keys + ' ' + pop['시도'][n]
                        elif pop['시도'][n] in ['마산합포구', '마산회원구']:
                            si_name[n] = keys + ' ' + pop['시도'][n][2:-1]
                        else:
                            si_name[n] = keys + ' ' + pop['시도'][n][:-1]

            elif pop['광역시도'][n] == '세종특별자치시':
                si_name[n] = '세종'

            else:
                if len(pop['시도'][n]) == 2:
                    si_name[n] = pop['광역시도'][n][:2] + ' ' + pop['시도'][n]
                else:
                    si_name[n] = pop['광역시도'][n][:2] + ' ' + pop['시도'][n][:-1]



if __name__ == '__main__':
    s=Solution()
    s.hook()