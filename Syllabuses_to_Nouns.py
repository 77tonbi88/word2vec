import MeCab
import requests
import re
import sys
import numpy as np
from bs4 import BeautifulSoup as BS
import csv


def make_mecab(target_url, fpass, dict):
    mecab = MeCab.Tagger()
    ban_word = ('(', ')', '（', '）', ':', '))(', ')(')
    id_pattern = re.compile(r'subject_id=([\d]{4})')
    nounAndVerb = []  # 「名詞」を格納するリスト
    soup = BS(requests.get(target_url).text, features="html.parser")
    # テキストファイルから空白文字を消去したい
    processed = soup.get_text().splitlines()
    processed_text = ''
    write_bool = False
    name = id_pattern.search(target_url)
    if not name:
        print('can not get')
        return 0
    for X in processed:
        if '//<![CDATA[' in X or '評価割合' == X:
            write_bool = False
        if X == '':  # 空白行を省く
            continue
        if '到達目標' == X or write_bool:
            write_bool = True
            processed_text += X.strip() + '\n'
    # URL先から取得した本文をmecabによって処理
    lines = mecab.parse(processed_text).split('\n')
    for line in lines:
        feature = line.split('\t')
        if len(feature) == 2:  # 'EOS'と''を省く
            info = feature[1].split(',')
            hinshi = info[0]
            if (hinshi in '名詞') and (info[1] not in '数') and (feature[0] not in ban_word):
                if feature[1] in '名詞,サ変接続,*,*,*,*,*':
                    continue  # 「①、②」等の主に記号である雑音的単語を削除
                # print(feature)
                nounAndVerb.append(feature[0])
    result = '\n'.join(nounAndVerb)
    '''
    with open(fpass+'base/'+name[1]+'_'+dict[name[1]]+'.txt', mode='w', encoding='utf-8') as fw:
        fw.write(processed_text)  # シラバスファイルの保存
    with open(fpass+name[1]+'_'+dict[name[1]]+'.txt', mode='w', encoding='utf-8') as fw:
        fw.write(result)  # 名詞のみファイルの保存
    '''


def main():
    file_pass = 'syllabuses/'
    base_url = 'https://syllabus.kosen-k.go.jp/Pages/PublicSubjects?school_id=21&department_id=03&year=2020'
    target_urls = []
    number_pattern = re.compile(r'subject_id=([\d]{4})')
    id_name_dict = {}
    # 自作関数make_mecabを行列式のデータに適用できる関数に変換
    all_make_mecab = np.frompyfunc(make_mecab, 3, 0)

    base_html = requests.get(base_url).text
    soup = BS(base_html, features="html.parser")
    link = soup.find_all('a', class_='mcc-show')
    # print(link)
    for line in link:
        number = number_pattern.search(str(line))
        id_name_dict[number[1]] = line.string
        target_urls.append('https://syllabus.kosen-k.go.jp' + line.get('href'))
    # print(len(id_name_dict))
    link_senmon = soup.find_all('td', class_='c2')
    print(link_senmon)
    '''
    with open("id_name_dict.csv", 'w') as file:
        writer = csv.DictWriter(file, id_name_dict.keys())
        writer.writeheader()
        writer.writerow(id_name_dict)
    '''
    # all_make_mecab(target_urls, file_pass, id_name_dict)
    print("終了")


if __name__ == '__main__':
    main()
