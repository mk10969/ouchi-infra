# ouchi-ansible

- Prerequisites  

  1. install on ansible execution host
  ``` 
  pip install ansible
  ```
    - required python >= 3
    - required ansible >= 2.9

  2. ping to target hosts
  ```
  $ ansible-playbook -i inventories/hosts playbooks/ping.yaml
  ```


- Run only for first time  

  apt update & upgrade  
```
$ ansible-playbook -i inventories/hosts playbooks/apt-upgrade.yaml
```


- Bootstrap kubernetes cluster  
  
  OS setup and installing Kubernetes with deployment tools  
```
$ ansible-playbook -i inventories/hosts playbooks/k8s-bootstrap.yaml
```
