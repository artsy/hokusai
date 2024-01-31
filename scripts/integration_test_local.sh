# run integration tests locally

export K8S_VERSION=v1.21.14
export KUBE_CONFIG_PATH=${HOME}/.kube/config
export KUBE_CONFIG_BACKUP_PATH=${HOME}/.kube/config.bak
export BACKED_UP_KUBE_CONFIG=false

function start_minikube(){
  profile=$1
  minikube delete --profile "$profile"
  minikube start --profile "$profile" --kubernetes-version="$K8S_VERSION"
  JSONPATH='{range .items[*]}{@.metadata.name}:{range @.status.conditions[*]}{@.type}={@.status};{end}{end}';
  until kubectl --context "$profile" get nodes -o jsonpath="$JSONPATH" 2>&1 | grep -q "Ready=True"; do
    sleep 1;
  done
}

if ls "$KUBE_CONFIG_PATH"
then
  echo "Backing up $KUBE_CONFIG_PATH ..."
  mv "$KUBE_CONFIG_PATH" "$KUBE_CONFIG_BACKUP_PATH"
  export BACKED_UP_KUBE_CONFIG=true
fi

start_minikube staging
start_minikube production

coverage run -m pytest test/integration

minikube stop --profile staging
minikube stop --profile production

if [ "$BACKED_UP_KUBE_CONFIG" = "true" ]
then
  echo "Restoring $KUBE_CONFIG_PATH ..."
  mv "$KUBE_CONFIG_BACKUP_PATH" "$KUBE_CONFIG_PATH"
fi