# ouchi-ansible

playbook become=yesは、sudoの意味。


- ping command  

cat ~/inventories/hosts 
で標準出力されたhostに対して、接続可能かpingを打つ。

```
$ ansible-playbook -i inventories/hosts playbooks/ping.yaml
```
