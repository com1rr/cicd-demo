# DevOps CI/CD Demo: GitHub Actions + Aliyun ACR + Kubernetes

这是一个基于 **GitHub Actions + 阿里云容器镜像服务 ACR + Kubernetes 三节点集群** 的云上 CI/CD 实践项目。

项目实现了从代码提交到自动测试、自动构建 Docker 镜像、推送镜像仓库、部署到 Kubernetes、滚动更新以及失败回滚的完整流程。

---

## 1. 项目目标

本项目用于学习和实践一套完整的云原生 DevOps 部署链路：

```text
开发者提交代码
↓
GitHub Actions 自动触发
↓
运行 Python 单元测试
↓
构建 Docker 镜像
↓
推送到阿里云 ACR
↓
SSH 到 Kubernetes master 节点
↓
执行 kubectl set image
↓
Kubernetes 滚动更新 Pod
↓
部署失败时自动 rollback

2. 技术栈
类型	技术
应用框架	Python Flask
WSGI Server	Gunicorn
容器化	Docker
镜像仓库	Aliyun ACR
编排平台	Kubernetes
集群初始化	kubeadm
容器运行时	containerd
CNI 网络	Calico
CI/CD	GitHub Actions
云服务器	Aliyun ECS
部署方式	SSH + kubectl rollout

3. 项目结构
cicd-demo/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── requirements.txt
├── tests/
│   └── test_app.py
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── Dockerfile
├── .dockerignore
└── README.md

4. 应用说明

Flask 应用位于：

app/main.py

示例代码：

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello DevOps CI/CD Demo!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

容器启动方式：

CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]

5. CI 测试

测试文件位于：

tests/test_app.py

测试逻辑：

from app.main import app

def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello DevOps" in response.data

GitHub Actions 会先执行：

pytest tests/

只有测试通过后，才会继续构建镜像并部署。

6. Docker 镜像构建

Dockerfile：

FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.main:app"]

.dockerignore 用于减少 Docker build context：

.git
.github
tests
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.env
.venv
venv
node_modules
README.md
*.md
7. Kubernetes 部署
Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devops-cicd-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: devops-cicd-demo
  template:
    metadata:
      labels:
        app: devops-cicd-demo
    spec:
      imagePullSecrets:
        - name: acr-secret
      containers:
        - name: devops-cicd-demo
          image: <ALIYUN_ACR_REGISTRY>/devops-cicd-demo/devops-cicd-demo:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 5000
Service
apiVersion: v1
kind: Service
metadata:
  name: devops-cicd-demo-service
spec:
  type: NodePort
  selector:
    app: devops-cicd-demo
  ports:
    - port: 80
      targetPort: 5000
      nodePort: 30080

访问方式：

http://<MASTER_PUBLIC_IP>:30080
8. GitHub Actions CI/CD 流程

Workflow 文件：

.github/workflows/ci-cd.yml

核心流程：

test job
  ↓
build-and-deploy job
CI 阶段
test:
  runs-on: ubuntu-latest

  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r app/requirements.txt

    - name: Run tests
      run: |
        PYTHONPATH=$GITHUB_WORKSPACE pytest tests/
CD 阶段
build-and-deploy:
  runs-on: ubuntu-latest
  needs: test

needs: test 表示只有测试成功，才会继续执行构建和部署。

9. Docker Build Cache 优化

项目使用 GitHub Actions 的 Docker layer cache：

cache-from: type=gha
cache-to: type=gha,mode=max

作用：

复用 Docker 构建缓存
减少重复 pip install
加快 Docker build 阶段

实际优化后，CI/CD 总耗时从约 80 秒降低到约 56 秒。

10. 自动部署与回滚

部署阶段通过 SSH 登录 Kubernetes master 节点，然后执行：

kubectl set image deployment/devops-cicd-demo \
  devops-cicd-demo=<IMAGE_NAME>:<COMMIT_SHA> \
  -n default

随后检查滚动更新状态：

kubectl rollout status deployment/devops-cicd-demo -n default --timeout=120s

如果部署失败，自动执行：

kubectl rollout undo deployment/devops-cicd-demo -n default

这样可以避免错误版本长时间影响线上服务。

11. GitHub Secrets 配置

GitHub Actions 中需要配置以下仓库机密：

Secret 名称	用途
ALIYUN_USERNAME	阿里云 ACR 用户名
ALIYUN_PASSWORD	阿里云 ACR 密码
K8S_HOST	Kubernetes master 公网 IP
K8S_USER	SSH 登录用户，例如 root
SSH_PRIVATE_KEY	GitHub Actions 登录 master 的 SSH 私钥

配置路径：

GitHub Repository
→ Settings
→ Secrets and variables
→ Actions
→ Repository secrets

注意：不要把密码、私钥、kubeconfig、token 提交到 GitHub 仓库。

12. 云服务器与 Kubernetes 集群

集群部署在阿里云 ECS 上：

k8s-master
k8s-worker1
k8s-worker2

节点之间通过私网通信。

Kubernetes 集群组件：

containerd
kubeadm
kubelet
kubectl
Calico CNI

由于国内访问 registry.k8s.io 和 quay.io 可能不稳定，本项目使用了阿里云 ACR 作为镜像中转仓库。

13. 遇到的问题与解决方案
13.1 registry.k8s.io 镜像拉取超时

问题：

kubeadm init 时拉取 registry.k8s.io 镜像超时

解决：

kubeadm init \
  --image-repository=registry.aliyuncs.com/google_containers
13.2 pause 镜像拉取失败

问题：

containerd 仍然尝试拉取 registry.k8s.io/pause

解决：

修改 containerd 配置中的 sandbox image：

registry.aliyuncs.com/google_containers/pause
13.3 Calico 镜像拉取失败

问题：

quay.io/calico 镜像拉取失败

解决：

将 Calico 镜像手动拉取、重新 tag，并推送到自己的阿里云 ACR。

13.4 私有 ACR 镜像拉取失败

问题：

ImagePullBackOff
insufficient_scope: authorization failed

解决：

在对应 namespace 创建 imagePullSecret：

kubectl create secret docker-registry acr-secret \
  --docker-server=<ALIYUN_ACR_REGISTRY> \
  --docker-username=<USERNAME> \
  --docker-password=<PASSWORD> \
  --docker-email=<EMAIL> \
  -n default
13.5 GitHub Actions 无法直接访问内网 K8s API

问题：

GitHub Actions runner 无法访问 Kubernetes 内网 API Server

解决：

采用 SSH 方式：

GitHub Actions
↓
SSH 到 master 公网 IP
↓
在 master 本机执行 kubectl
14. 本项目学习收获

通过这个项目，完成了以下 DevOps 核心能力训练：

1. 使用 kubeadm 搭建三节点 Kubernetes 集群
2. 使用 containerd 作为容器运行时
3. 使用 Calico 配置 K8s 网络
4. 使用阿里云 ACR 管理私有镜像
5. 编写 Dockerfile 构建 Python Flask 镜像
6. 使用 GitHub Actions 进行自动测试
7. 使用 Docker Build Cache 优化构建速度
8. 使用 GitHub Secrets 管理敏感信息
9. 使用 SSH + kubectl 自动部署到 K8s
10. 使用 rollout status 和 rollout undo 实现部署检查与回滚
15. 当前 CI/CD 链路总结
Developer
  ↓ git push
GitHub Repository
  ↓ trigger workflow
GitHub Actions
  ↓ pytest
Docker Buildx
  ↓ build image
Aliyun ACR
  ↓ push image
Kubernetes Master
  ↓ kubectl set image
Kubernetes Workers
  ↓ pull image and run pods
NodePort Service
  ↓
Browser
16. 后续可优化方向

后续可以继续扩展：

1. dev / prod 多环境部署
2. Pull Request 自动测试
3. GitHub Environments 审批发布
4. Helm 管理 Kubernetes 配置
5. Ingress + 域名访问
6. HTTPS 证书配置
7. Self-hosted Runner 加速构建
8. Prometheus + Grafana 监控
9. 日志采集与告警
17. 项目状态

当前状态：

CI 测试：已完成
Docker 镜像构建：已完成
ACR 推送：已完成
K8s 自动部署：已完成
失败回滚：已完成
构建缓存优化：已完成

这是一个完整的云上 Kubernetes CI/CD Demo。


保存后提交：

```bash
git add README.md
git commit -m "add project readme"
git push origin main
