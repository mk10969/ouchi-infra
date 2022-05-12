# Raspberry Pi Zero WH

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


2. ログイン
```
$ ssh pi@raspberrypi.local
password raspberry
```


3. ユーザの作成
```
sudo su -
useradd -m ubuntu
passwd ubuntu 
```


4. グループの追加
```
$ groups pi
```
```
$ sudo usermod -G adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,render,netdev,spi,i2c,gpio,lpadmin ubuntu
```


5. ssh keyの作成
```
$ ssh-keygen -t rsa -b 4096
```


6. no password (非推奨)
```
ubuntu ALL=(ALL) NOPASSWD: ALL
```
TODO: ansible-vault


7. nginx.conf 
コメアウト
```
	# include /etc/nginx/sites-enabled/*;
```

8. wifi power management off
https://geek.tacoskingdom.com/blog/38
https://elsammit-beginnerblg.hatenablog.com/entry/2021/02/16/213737

## IR recording
下記のコマンドを実行後、赤外線センサーをデバイスに向かって照射する
python3 /<Path>/irrp.py -r -g4 -f <FilePath> light::on --no-confirm --post 130

