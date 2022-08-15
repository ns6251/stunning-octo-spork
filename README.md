# stunning-octo-spork

## Pre-requirements

- Python 3.10 or later
- Poetry

## インストール方法

```
git clone https://github.com/ns6251/stunning-octo-spork.git
cd stunning-octo-spork
poetry install
```

## 使い方

```
poetry run python -m stunning_octo_spork -h
usage: __main__.py [-h] [-n [N]] [-m [M]] [-t [T]] [path]

監視ログの統計

positional arguments:
  path        読み込む監視ログのパス

options:
  -h, --help  show this help message and exit
  -n [N]      故障判定に必要な連続タイムアウトの回数（デフォルト: 1）
  -m [M]      過負荷判定に用いる直近の回数（デフォルト: 1）
  -t [T]      過負荷判定の平均応答時間の閾値（デフォルト: 500 [ms]）
```

## テスト

### ユニットテスト

ユニットテストは `/tests` ディレクトリにある．
ユニットテストには，pytestを利用した．

### システムテスト

- 入力: log.csv
- 出力結果: answer.csv

実行コマンド

```
poetry run python -m stunning_octo_spork log.csv -n 1 -m 3 -t 500 > answer.csv
```

## 内容

設問1から設問4までの実装はすべて1つのパッケージに実装されている．主なロジックはdetect.pyにある．
2つあるDetectorに1件ずつログをパースした結果を追加させ，全て追加が終わったら検出したものをまとめる仕組みである．
想定として，入力されるログは時系列で降順になっている．
また，結果は標準出力に出力される．

### 出力フォーマット

```
<種類>,<サーバーアドレス>,<開始時刻>,<終了時刻>
```

種類は，`down`（故障，停止）か `overload`（過負荷）かのいずれかである．
サーバアドレスは，ネットワークプレフィックス長付きのIPv4アドレスである．スイッチの故障の場合はネットワークアドレスになっている．
開始時刻，終了時刻のフォーマットはYYYYMMDDhhmmssの形式である．また，終了時刻は `-`になりうる（正常に戻らなかった場合）．
