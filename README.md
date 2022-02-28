# ouchi-ansible

raspi 4 model B
OS: ubuntu 20.04.3 LTS (Focal Fossa)

raspi zero w
OS: Raspbian GNU/Linux 11 (bullseye)

## Prerequisites  

- write boot image  
[setup raspi 4](https://qiita.com/HeRo/items/c1c30d7267faeb304538
)  
[setup raspi zero](https://qiita.com/hishi/items/8bdfd9d72fa8fe2e7573)

- install ansible on execution host
  ``` 
  pip install ansible
  ```
  | package | required version |
  | ------- | ---------------- |
  | python  | >=3              |
  | ansible | >= 2.9           |


- ping to target hosts
  ```
  $ ansible-playbook -i inventories/hosts playbooks/ping.yaml
  ```

- when using [rook/ceph](https://rook.io/docs/rook/v1.6/ceph-quickstart.html#prerequisites)  , prepare raw device and fresh raw device on kubernetes workers

  ```
  $ ansible-playbook -i inventories/hosts playbooks/dev-fresh.yaml
  ```


## Run only for first time  

apt update & upgrade.  

```
$ ansible-playbook -i inventories/hosts playbooks/apt-upgrade.yaml
```


## Bootstrap kubernetes cluster  

setup OS, installing kubernetes with deployment tools and bootstrap kubernetes cluster.  

```
$ ansible-playbook -i inventories/hosts playbooks/k8s-bootstrap.yaml
```

## Deployment Argo CD

Argo CD is a declarative, GitOps continuous delivery tool for kubernetes.

```
$ ansible-playbook -i inventories/hosts playbooks/k8s-deploy-argocd.yaml
```
