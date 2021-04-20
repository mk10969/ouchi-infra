# ouchi-ansible

- Prerequisites  

1. install on ansible execution host
    ``` 
    pip install ansible
    ```
    | package | required version |
    | ------- | ---------------- |
    | python  | >=3              |
    | ansible | >= 2.9           |


2. ping to target hosts
    ```
    $ ansible-playbook -i inventories/hosts playbooks/ping.yaml
    ```

3. [rook/ceph](https://rook.io/docs/rook/v1.6/ceph-quickstart.html#prerequisites)  

    prepare raw device.

4. raw device fresh on k8s-workers
    ```
    $ ansible-playbook -i inventories/hosts playbooks/dev-fresh.yaml
    ```


- Run only for first time  

  apt update & upgrade.  
    ```
    $ ansible-playbook -i inventories/hosts playbooks/apt-upgrade.yaml
    ```


- Bootstrap kubernetes cluster  
  
  OS setup and installing kubernetes with deployment tools.  
    ```
    $ ansible-playbook -i inventories/hosts playbooks/k8s-bootstrap.yaml
    ```
