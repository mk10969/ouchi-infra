# About Infra Red

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




## IR recording

python3 irrp.py -r -g4 -f codes light::on --no-confirm --post 130
python3 irrp.py -r -g4 -f codes2 light::off --no-confirm --post 130
python3 irrp.py -r -g4 -f codes5 light::dark --no-confirm --post 130
python3 irrp.py -r -g4 -f codes6 light::bright --no-confirm --post 130
python3 irrp.py -r -g4 -f codes7 light::warm --no-confirm --post 130
python3 irrp.py -r -g4 -f codes8 light::white --no-confirm --post 130
python3 irrp.py -r -g4 -f codes3 aircon::on --no-confirm --post 130
python3 irrp.py -r -g4 -f codes4 aircon::off --no-confirm --post 130


## IR sending
python3 irrp.py -p -g13 -f codes light::on
python3 irrp.py -p -g13 -f codes2 light::off
python3 irrp.py -p -g13 -f codes5 light::dark
python3 irrp.py -p -g13 -f codes6 light::bright
python3 irrp.py -p -g13 -f codes7 light::warm
python3 irrp.py -p -g13 -f codes8 light::white


## 無駄なサービスを停止する
 - 一覧表示
```
systemctl list-units --type=service
```
 - 停止
```
sudo systemctl stop keyboard-setup
sudo systemctl disable keyboard-setup

sudo systemctl stop kbd
sudo systemctl disable kbd

sudo swapoff --all
sudo systemctl stop dphys-swapfile
sudo systemctl disable dphys-swapfile

sudo systemctl stop plymouth
sudo systemctl disable plymouth

```


sudo systemctl stop dhcpcd
sudo systemctl disable dhcpcd

