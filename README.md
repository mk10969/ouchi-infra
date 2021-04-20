# ouchi-ansible

## Prerequisites  

- install on ansible execution host
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

- whon using [rook/ceph](https://rook.io/docs/rook/v1.6/ceph-quickstart.html#prerequisites)  , prepare raw device and fresh raw device on k8s-workers

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

Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes.

```
$ ansible-playbook -i inventories/hosts playbooks/k8s-deploy-argocd.yaml
```
