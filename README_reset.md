# kuberntes cluster clean up

- ref
https://kubernetes.io/ja/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/#tear-down


http://tjtjtj.hatenablog.com/entry/2019/02/13/230000


- get nodes
```
kubectl get nodes | cut -d " " -f 1 | grep -v "NAME"
```

- drain node 
```
kubectl drain raspi4-03 --delete-local-data --force --ignore-daemonsets

kubectl drain raspi4-02 --delete-local-data --force --ignore-daemonsets


```

- delete node
```
kubectl delete node raspi4-03
kubectl delete node raspi4-02
```

- reset
```
kubeadm reset
```

kubectl drain raspi4-01 --delete-local-data --force --ignore-daemonsets

kubectl delete node raspi4-01
