# Raspberry Pi Zero WH

### TODO
enable SSL (Let's Encrypt) 

## init
https://nw-electric.way-nifty.com/blog/2022/05/post-2cdd01.html
2022年より、デフォルトユーザ`pi`が削除された。
なので、raspberry Pi imagerでGUIより、下記を作成する
- hostname
- user
- wifi


1. ログイン
```
$ ssh <username>@<hostname>.local
```

2. authorized_keys作成
```
$ mkdir .ssh/
$ touch .ssh/authorized_keys
```

3. nginx.conf 
コメアウト
```
	# include /etc/nginx/sites-enabled/*;
```

4. wifi power management off
https://hnw.hatenablog.com/entry/2020/10/11/134737


## get irrp.py
curl http://abyz.me.uk/rpi/pigpio/code/irrp_py.zip > irrp.py.zip

## IR recording
下記のコマンドを実行後、赤外線センサーをデバイスに向かって照射する
python3 /<Path>/irrp.py -r -g4 -f <FilePath> light::on --no-confirm --post 130

## IR sending
python3 /<Path>/send.py -g13 -f codes.json light::on

## CUIで起動
メモリ節約のため、GUIではなくCUIで起動する。
https://www.lisz-works.com/entry/raspi0-conifg
https://www.dogrow.net/linux/blog75/
