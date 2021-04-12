### env path

# k8s
set -x KUBECONFIG $HOME/.kube/config

# set -x LANGUAGE ja_JP.UTF-8
# set -x LC_ALL ja_JP.UTF-8
# set -x LANG ja_JP.UTF-8
# set -x LC_TYPE ja_JP.UTF-8

# # golang
# set -x GOPATH $HOME/go
# set -x PATH $GOPATH/bin $PATH

# # Kustomize
# set -x PATH $HOME/kustomize $PATH

### theme
starship init fish | source

### alias
alias ll='ls -la'

alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
