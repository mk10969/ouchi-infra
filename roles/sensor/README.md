# About Infra Red

### TODO
enable SSL (Let's Encrypt) 

## init

1. wifiの設定
SDカードにOSイメージを書き込んだあとで
```
wpa_supplicant.conf
```
と空ファイルの
```
ssh
```
を、/Volumes/boot/にコピーする

2. ユーザの作成
ssh pi@xxx.xxx.xxx.xxx
で、ログインし、ubuntuユーザを作成する
```
sudo su -
useradd -m ubuntu
passwd ubuntu 
```

3. sudoグループ追加とNo password設定

4. nginx.conf 
コメアウト
```
	# include /etc/nginx/sites-enabled/*;
```


## IR recording
下記のコマンドを実行後、赤外線センサーをデバイスに向かって照射する
python3 /<Path>/irrp.py -r -g4 -f codes light::on --no-confirm --post 130
