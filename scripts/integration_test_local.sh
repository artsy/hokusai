### run integration tests locally


## requirements

# - awscli
# - coverage
# - docker
# - jq
# - kubectl
# - minikube
# - pytest


## prepare env

export K8S_VERSION=v1.21.14
export KUBE_CONFIG_PATH=${HOME}/.kube/config
export KUBE_CONFIG_BACKUP_PATH=${HOME}/.kube/config.bak
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
export AWS_REGION=$(aws configure get region)
export DOCKER_CONFIG_JSON_PATH=${HOME}/.docker/config.json


## functions

function start_minikube() {
  profile=$1
  minikube delete --profile "$profile"
  minikube start --profile "$profile" --kubernetes-version="$K8S_VERSION"
  JSONPATH='{range .items[*]}{@.metadata.name}:{range @.status.conditions[*]}{@.type}={@.status};{end}{end}';
  until kubectl --context "$profile" get nodes -o jsonpath="$JSONPATH" 2>&1 | grep -q "Ready=True"; do
    sleep 1;
  done
}

function create_real_docker_config_json() {
  # on Mac, Docker config.json points to credsStore
  # where the creds are really stored,
  # create a file that has the creds inline
  local dockercfg=$(mktemp ~/.docker/config.json.XXX)
  local storetype=$(jq -r .credsStore < $DOCKER_CONFIG_JSON_PATH)
  local registry=''
  (
    echo '{'
    echo '    "auths": {'
    for registry in $(docker-credential-$storetype list | jq -r 'to_entries[] | .key'); do
      if [ ! -z "$FIRST" ]; then
          echo '        },'
      fi
      FIRST='true'
      credential=$(echo $registry | docker-credential-$storetype get | jq -jr '"\(.Username):\(.Secret)"' | base64)
      echo '        "'$registry'": {'
      echo '            "auth": "'$credential'"'
    done
    echo '        }'
    echo '    }'
    echo '}'
  ) > $dockercfg
  echo "$dockercfg"
}

function back_up_kube_config() {
  # don't let minikube overwrite user's real k8s kubeconfig
  local backed_up_kube_config=''
  if ls "$KUBE_CONFIG_PATH"
  then
    echo "Backing up $KUBE_CONFIG_PATH ..."
    mv "$KUBE_CONFIG_PATH" "$KUBE_CONFIG_BACKUP_PATH"
    backed_up_kube_config='true'
  fi
  echo "$backed_up_kube_config"
}

function restore_kube_config() {
  echo "Restoring $KUBE_CONFIG_PATH ..."
  mv "$KUBE_CONFIG_BACKUP_PATH" "$KUBE_CONFIG_PATH"
}

function create_regcred() {
  # create ecr image pull secret in minikube/k8s
  aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS \
      --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
  local dockercfg=$(create_real_docker_config_json)
  # ensure file is deleted when script exits
  trap "rm -f $dockercfg" EXIT
  create_regcred_for_env 'staging' $dockercfg
  create_regcred_for_env 'production' $dockercfg
  rm -f "$dockercfg"
}

function create_regcred_for_env() {
  local environment=$1
  local dockercfg=$2
  kubectl --context "$environment" create secret generic regcred \
    --from-file=.dockerconfigjson="$dockercfg" \
    --type=kubernetes.io/dockerconfigjson
  kubectl --context "$environment" patch serviceaccount default -p '{"imagePullSecrets": [{"name": "regcred"}]}'
}


## main

kube_config_is_backed_up=$(back_up_kube_config)
start_minikube staging
start_minikube production
create_regcred
coverage run -m pytest test/integration
minikube stop --profile staging
minikube stop --profile production
if [ "$kube_config_is_backed_up" = "true" ]
then
  restore_kube_config
fi
