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
