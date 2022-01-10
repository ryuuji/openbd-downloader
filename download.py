"""
openBDから公開されているすべての情報を取得するサンプル
テスト環境 : Python3.10.1
"""

import multiprocessing
import time
import requests
from more_itertools import chunked

OPENBD_ENDPOINT = 'https://api.openbd.jp/v1/'


def get_coverage():
    """
    openBDから収録ISBNの一覧を取得
    :return: ISBNのリスト
    """
    return requests.get(OPENBD_ENDPOINT + 'coverage').json()


def get_bibs(items: list[str]) -> dict:
    """
    openBDからPOSTでデータを取得する
    :param items: ISBNのリスト
    :return: 書誌のリスト
    """
    return requests.post(OPENBD_ENDPOINT + 'get', data={'isbn': ','.join(items)}).json()


if __name__ == '__main__':

    # ISBNのリストを10000件単位に分割
    chunked_coverage = chunked(get_coverage(), 10000)

    # 4プロセスの並列でダウンロード
    # マジックナンバー: 事後処理の並列性にあわせて調整
    p = multiprocessing.Pool(4)
    results = p.imap_unordered(get_bibs, chunked_coverage)
    count = 0
    start = time.time()
    for result in results:
        for bib in result:
            # Coverageにあっても、実データがない場合（Noneが返る）を想定する
            # （複数サーバーのデータ同期が遅れる場合があるため）
            if bib is None:
                continue
            # ここで書誌1件単位の処理
            count += 1
            if count % 1000 == 0:
                print(count, bib['summary']['isbn'], bib['summary']['title'])  # サンプルのタイトルを表示

    print(count, time.time() - start)
