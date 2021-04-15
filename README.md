# ouchi-ansible

- Prerequisites  

  1. install  
  ``` 
  pip install ansible
  ```
    - required python >= 3
    - required ansible >= 2.9


  1. ping
  ```
  $ ansible-playbook -i inventories/hosts playbooks/ping.yaml
  ```

- setup (for k8s cluster)
```
$ ansible-playbook -i inventories/hosts playbooks/common.yaml
$ ansible-playbook -i inventories/hosts playbooks/k8s-setup.yaml
$ ansible-playbook -i inventories/hosts playbooks/reboot.yaml
```
- create k8s cluster
```
$ ansible-playbook -i inventories/hosts playbooks/k8s-init.yaml
```


kubeadm init済みであれば、return code=1
kubeadm join済みであれば、return code=1


### TODO
fishのカラー設定を加える。
k8s cluster お掃除role and playbook
