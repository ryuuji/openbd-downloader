#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
openBDから公開されているすべての情報を取得するサンプル
テスト環境 : Python2.7.12
依存モジュール : requests (pip install requests)
"""

import multiprocessing
import requests


def chunked(iterable, n):
    """
    リストをn個単位のリストに分割する
    http://cortyuming.hateblo.jp/entry/2015/12/26/091224
    """
    return [iterable[x:x + n] for x in range(0, len(iterable), n)]


def get_bibs(items):
    """
    openBDからPOSTでデータを取得する
    :param items: ISBNのリスト
    :return: 書誌のリスト
    """
    return requests.post('http://api.openbd.jp/v1/get', data={'isbn': ','.join(items)}).json()


if __name__ == '__main__':

    # openBDから収録ISBNの一覧を取得
    coverage = requests.get('http://api.openbd.jp/v1/coverage').json()

    # 10000件単位に分割
    chunked_coverage = chunked(coverage, 10000)

    # 4プロセスの並列でダウンロード
    # マジックナンバー:openBDインフラ的に4接続が最適
    p = multiprocessing.Pool(4)
    results = p.imap_unordered(get_bibs, chunked_coverage)

    for result in results:
        for bib in result:
            # ここで書誌1件単位の処理　exp:インデックス化など
            if bib:
                # Coverageにあっても、実データがない場合（Noneが返る）を想定すること
                # （複数サーバーのデータ同期が遅れる場合があるため）
                print bib['summary']['isbn']
