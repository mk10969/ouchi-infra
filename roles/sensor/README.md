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
https://geek.tacoskingdom.com/blog/38
https://elsammit-beginnerblg.hatenablog.com/entry/2021/02/16/213737



## IR recording
下記のコマンドを実行後、赤外線センサーをデバイスに向かって照射する
python3 /<Path>/irrp.py -r -g4 -f <FilePath> light::on --no-confirm --post 130

## IR sending
python3 /<Path>/irrp.py -p -g17 -f codes.json light:on