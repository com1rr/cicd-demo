# DevOps CI/CD Demo

这是一个基于 **GitHub Actions + Docker + 阿里云 ACR + Kubernetes** 的云上 CI/CD 实践项目。

项目实现了从代码提交、自动测试、自动构建镜像、推送镜像仓库，到自动部署到 Kubernetes 集群的完整流程。

---

## 项目目标

本项目用于学习和实践一套完整的 DevOps 自动化部署链路：

```text
代码提交
↓
GitHub Actions 自动触发
↓
运行 pytest 自动测试
↓
构建 Docker 镜像
↓
推送镜像到阿里云 ACR
↓
SSH 登录 Kubernetes master 节点
↓
执行 kubectl set image
↓
Kubernetes 滚动更新 Pod
↓
部署失败自动回滚
技术栈
Python Flask
Gunicorn
Docker
GitHub Actions
阿里云 ACR
Kubernetes
kubeadm
containerd
Calico CNI
阿里云 ECS
项目结构
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
CI/CD 流程

本项目的 GitHub Actions workflow 分为两个主要阶段。

1. CI：自动测试

每次代码提交后，GitHub Actions 会先执行测试：

拉取代码
↓
安装 Python 环境
↓
安装依赖
↓
运行 pytest

如果测试失败，后续的镜像构建和 Kubernetes 部署不会继续执行。

2. CD：自动构建与部署

测试通过后，进入部署流程：

登录阿里云 ACR
↓
使用 Docker Buildx 构建镜像
↓
推送镜像到阿里云 ACR
↓
SSH 登录 Kubernetes master
↓
更新 Deployment 镜像
↓
等待 Kubernetes 滚动更新完成

部署过程中会检查 rollout 状态。如果新版本部署失败，会自动执行回滚。

Kubernetes 部署方式

应用通过 Kubernetes Deployment 部署，副本数为 2。

服务通过 NodePort 暴露：

NodePort: 30080

访问方式：

http://<服务器公网IP>:30080
GitHub Secrets

项目需要在 GitHub 仓库中配置以下 Secrets：

Secret 名称	用途
ALIYUN_USERNAME	阿里云 ACR 用户名
ALIYUN_PASSWORD	阿里云 ACR 密码
K8S_HOST	Kubernetes master 节点公网 IP
K8S_USER	SSH 登录用户
SSH_PRIVATE_KEY	GitHub Actions SSH 登录 master 的私钥

敏感信息不会写入代码仓库，而是通过 GitHub Secrets 管理。

已实现功能
Flask 应用容器化
Docker 镜像自动构建
镜像推送到阿里云 ACR
Kubernetes 自动滚动更新
pytest 自动测试
测试通过后才允许部署
Docker Build Cache 构建加速
.dockerignore 优化构建上下文
SSH 远程部署到 K8s master
部署失败自动回滚
项目学习收获

通过本项目，实践了以下内容：

使用 kubeadm 搭建三节点 Kubernetes 集群
使用 containerd 作为 Kubernetes 容器运行时
使用 Calico 配置集群网络
使用阿里云 ACR 管理私有镜像
使用 imagePullSecret 拉取私有镜像
编写 Dockerfile 构建 Flask 应用镜像
使用 GitHub Actions 实现 CI/CD
使用 Docker Buildx cache 优化构建速度
使用 kubectl rollout status 检查部署状态
使用 kubectl rollout undo 实现失败回滚
后续优化方向
使用 Helm 管理 Kubernetes 配置
增加 dev / prod 多环境部署
增加 Pull Request 自动测试
使用 GitHub Environment 做生产环境审批
配置 Ingress 和域名访问
接入 Prometheus + Grafana 监控
使用 self-hosted runner 提升构建速度
