# Copy labels to pods from nodes

Built with [Shell Operator](https://github.com/flant/shell-operator)

## Build & Deploy

### Docker Image

1. Copy `auto-labeler.py` into `docker`

1. docker build & push

### RBAC

~~~yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitor-pods
rules:
- resources:
  - pods
  verbs:
  - get
  - watch
  - list
  - patch
- resources:
  - nodes
  verbs:
  - get
  - watch
  - list
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitor-pods
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: monitor-pods
subjects:
- kind: ServiceAccount
  name: monitor-pods-acc
  namespace: example-monitor-pods
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: monitor-pods-acc
  namespace: example-monitor-pods
~~~

### Deployment

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: auto-labeler
  name: auto-labeler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: auto-labeler
  template:
    metadata:
      labels:
        app: auto-labeler
    spec:
      serviceAccountName: monitor-pods-acc
      containers:
      - image: dustise/auto-labeler:v0.0.1
        imagePullPolicy: IfNotPresent
        name: auto-labeler
        volumeMounts:
        - mountPath: /etc/auto-labeler/
          name: operator-config
      volumes:
      - configMap:
          name: auto-labeler-config
        name: operator-config
~~~

### ConfigMap

`kubectl create cm auto-labeler-config --from-file=config.yaml`

### Env

- **COPY_LABELS**：Labels on node will be copied to the pods.(default: `node-dc,node-rack,node-name`)

### config.yaml

- `matchExpressions`: Select specified pods to be labeled.  