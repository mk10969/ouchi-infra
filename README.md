# ouchi-ansible

- pre install
 
pip install ansible
pip install openshift

required python >= 3
required ansible >= 2.9
required openshift >= 0.6


- ping command  

cat ~/inventories/hosts 
で標準出力されたhostに対して、接続可能かpingを打つ。

```
$ ansible-playbook -i inventories/hosts playbooks/ping.yaml
```
