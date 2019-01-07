#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
openBDから公開されているすべての情報を取得するサンプル
テスト環境 : Python3.7.1
依存モジュール : requests (pip install requests)
"""

import multiprocessing
import time
import requests

OPENBD_ENDPOINT = 'https://api.openbd.jp/v1/'


def chunked(iterable, n):
    """
    リストをn個単位のリストに分割する
    http://cortyuming.hateblo.jp/entry/2015/12/26/091224
    """
    return [iterable[x:x + n] for x in range(0, len(iterable), n)]


def get_coverage():
    """
    openBDから収録ISBNの一覧を取得
    :return: ISBNのリスト
    """
    return requests.get(OPENBD_ENDPOINT + 'coverage').json()


def get_bibs(items):
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
    # マジックナンバー:openBDインフラ的に4接続が最適
    p = multiprocessing.Pool(4)
    results = p.imap_unordered(get_bibs, chunked_coverage)
    cnt = 0
    start = time.time()
    for result in results:
        cnt += len(result)
        print(cnt)
        for bib in result:
            # ここで書誌1件単位の処理　exp:インデックス化など
            if bib and 'summary' in bib:
                # Coverageにあっても、実データがない場合（Noneが返る）を想定すること
                # （複数サーバーのデータ同期が遅れる場合があるため）
                print(bib['summary']['isbn'])

    print(cnt,time.time()-start)
