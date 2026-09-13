# 实验包

网页教程是实验说明的主入口。需要真实 GPU/Kubernetes 的实验尚未在作者本机运行；不要将配置检查视作硬件复现。

- serving: 固定 vLLM 0.29.0，解析模型 commit，测量客户端首内容和 chunk 时间。
- attention: 无第三方依赖的小尺寸 K/V 复用证明。
- kernel: PyTorch 2.14.0 基线，实际安装 CUDA wheel 需匹配驱动；正确性先于测量。
- nccl: 两 rank AllReduce，PyTorch 自带 NCCL 版本从运行时打印，不假定等于独立 Device API 2.31.2。
- kubernetes: 1.37 基线，Device Plugin 与 DRA 是不同设备分配路径；DRA 类名必须适配已安装驱动。
- observability: 本地 Prometheus；指标名称从真实 /metrics HELP/TYPE 核对。
- rollouts: CPU 故障服务用于发布控制验证，不是推理性能模拟。

执行前记录硬件、驱动、软件版本、镜像 digest、模型 revision 和负载。所有资源在独立 inference-lab namespace 中使用；删除 namespace 会删除其中全部实验对象，先保存结果。
