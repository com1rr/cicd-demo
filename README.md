# DevOps CI/CD GitOps Demo

这是一个基于 **GitHub Actions + Docker + 阿里云 ACR + Kubernetes + Argo CD** 的云上 DevOps / GitOps 实践项目。

项目实现了从代码提交、自动测试、自动构建镜像、推送镜像仓库、自动更新 Kubernetes manifest，到 Argo CD 自动同步部署的完整流程。

---

## 项目目标

本项目用于学习和实践一套接近企业常见模式的云原生 CI/CD 链路：

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
自动更新 k8s/prod/deployment.yaml 中的镜像 tag
↓
提交 manifest 变更到 GitHub
↓
Argo CD 检测 Git 状态变化
↓
自动同步到 Kubernetes prod 环境
```
技术栈
```
Python Flask
Gunicorn
Docker
GitHub Actions
Docker Buildx Cache
阿里云 ACR
Kubernetes
kubeadm
containerd
Calico CNI
Argo CD
阿里云 ECS
```
项目结构
```text
cicd-demo/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── requirements.txt
├── tests/
│   └── test_app.py
├── k8s/
│   ├── dev/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── prod/
│       ├── deployment.yaml
│       └── service.yaml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── Dockerfile
├── .dockerignore
└── README.md
```
CI/CD 流程

本项目采用 GitHub Actions + Argo CD 的分工方式：
```
GitHub Actions：负责 CI、镜像构建、镜像推送、更新 Git 中的部署配置
Argo CD：负责监听 Git 中的 Kubernetes 配置，并同步到集群
```
1. CI：自动测试

每次向 main 分支提交代码后，GitHub Actions 会先执行测试：
```
拉取代码
↓
安装 Python 环境
↓
安装依赖
↓
运行 pytest
```
如果测试失败，后续 Docker 镜像构建和 manifest 更新不会继续执行。

2. Build：构建并推送镜像

测试通过后，GitHub Actions 会：
```
登录阿里云 ACR
↓
使用 Docker Buildx 构建镜像
↓
使用 commit hash 作为镜像 tag
↓
推送镜像到阿里云 ACR
```
镜像 tag 不再依赖 latest，而是使用 Git commit hash，例如：
```
devops-cicd-demo:69782e306e83126ce7a0c1daaf9b2d3c3dd58f25
```
这样可以明确追踪线上版本，也方便回滚。

3. GitOps：更新 Kubernetes Manifest

镜像推送完成后，GitHub Actions 会自动修改：
```
k8s/prod/deployment.yaml
```
将其中的镜像 tag 更新为本次构建的 commit hash。

然后 Actions 会把 manifest 变更提交回 GitHub。

4. CD：Argo CD 自动同步

Argo CD 监听 GitHub 仓库中的：
```
k8s/prod
```
当 deployment.yaml 发生变化后，Argo CD 会检测到 Git 中的期望状态与集群实际状态不一致，并自动同步到 Kubernetes 的 prod namespace。

当前 Argo CD 开启了：
```
Auto Sync
Self Heal
```
这意味着：

Git 中的配置变化后，Argo CD 会自动部署
如果集群资源被手动修改，Argo CD 会自动恢复为 Git 中声明的状态
Kubernetes 部署

应用部署在 Kubernetes 集群中。

生产环境 namespace：
```
prod
```
Deployment 副本数：
```
2
```
Service 类型：
```
NodePort
```
prod 环境访问端口：
```
30082
```
访问方式：
```
http://<服务器公网IP>:30082
```
GitHub Secrets

项目需要在 GitHub 仓库中配置以下 Secrets：

Secret 名称	用途
ALIYUN_USERNAME	阿里云 ACR 用户名
ALIYUN_PASSWORD	阿里云 ACR 密码

早期 SSH 部署版本中还使用过：

Secret 名称	用途
K8S_HOST	Kubernetes master 节点公网 IP
K8S_USER	SSH 登录用户
SSH_PRIVATE_KEY	GitHub Actions SSH 登录 master 的私钥

当前 GitOps 版本中，生产环境部署由 Argo CD 接管，GitHub Actions 不再直接 SSH 到 master 执行 kubectl。

已实现功能
```
Flask 应用容器化
pytest 自动测试
测试通过后才允许构建镜像
Docker Buildx 构建镜像
Docker layer cache 构建加速
.dockerignore 优化构建上下文
镜像推送到阿里云 ACR
使用 commit hash 作为镜像 tag
GitHub Actions 自动更新 Kubernetes manifest
Argo CD 监听 GitHub 仓库
Argo CD 自动同步到 Kubernetes
Argo CD Self Heal 自动修复集群漂移
Kubernetes prod namespace 独立部署
NodePort 暴露服务
```
当前发布链路
```
Developer
  ↓ git push
GitHub Repository
  ↓ trigger
GitHub Actions
  ↓ pytest
Docker Buildx
  ↓ build image
Aliyun ACR
  ↓ push image
Update k8s/prod/deployment.yaml
  ↓ commit manifest
GitHub Repository
  ↓ watched by Argo CD
Argo CD
  ↓ auto sync
Kubernetes prod namespace
  ↓ rolling update
Browser
```
传统 CI/CD 与 GitOps 的区别

早期版本中，本项目使用：
```
GitHub Actions
↓
SSH 到 Kubernetes master
↓
kubectl set image
```
这种方式可以跑通自动部署，但 GitHub Actions 需要直接操作集群。

当前版本改为 GitOps 模式：

GitHub Actions 只负责测试、构建镜像、更新 Git 中的 YAML
Argo CD 负责从 Git 同步到 Kubernetes 集群

这种方式的优势是：

Git 是部署状态的唯一来源
集群状态可以被 Argo CD 持续校验
部署过程更加声明式
不需要 CI 工具直接操作 Kubernetes master
更接近企业常见的 GitOps 发布模式
项目学习收获

通过本项目，实践了以下内容：

使用 kubeadm 搭建三节点 Kubernetes 集群
使用 containerd 作为 Kubernetes 容器运行时
使用 Calico 配置集群网络
使用阿里云 ACR 管理私有镜像
使用 imagePullSecret 拉取私有镜像
编写 Dockerfile 构建 Flask 应用镜像
使用 GitHub Actions 实现 CI 流程
使用 Docker Buildx cache 优化构建速度
使用 commit hash 管理镜像版本
使用 Argo CD 实现 GitOps CD
理解 Auto Sync、OutOfSync、Synced、Healthy、Self Heal 等概念
将部署方式从 SSH kubectl 升级为 Argo CD GitOps
后续优化方向
dev / prod 分支自动部署
使用 Helm 管理 Kubernetes 配置
使用 Ingress 替代 NodePort
配置域名和 HTTPS
GitHub Pull Request 自动测试
使用 GitHub Environment 做生产环境审批
接入 Prometheus + Grafana 监控
学习 Jenkins + Argo CD 企业流水线组合
