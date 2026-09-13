# 五个项目的实验源码

网页 `/projects/` 是完整实验说明。所有命令从仓库根目录执行。ZIP 仅包含 labs 源码，tests 请从仓库获取。

- tiny_model：7 token、两层 Transformer，训练/缓存/保存加载；CPU 已运行。
- distributed：DDP 全局批次对照、DCP 下一步恢复对照；CPU 双进程已运行。FSDP2 CUDA 路径未运行。
- single_training：固定 Qwen3-0.6B revision 的 LoRA；CUDA BF16 路径未运行。
- kernel：Triton 尾块与加法正确性、计时、编译/优化器比较；GPU 未运行。
- serving：vLLM 0.29.0、Qwen3-0.6B 固定 revision；流式客户端和主动取消。真实 GPU 服务未运行。
- nccl：多 rank collective 检查；CUDA/NCCL 未运行。
- kubernetes：Kubernetes 1.36 基线，训练 Job/PVC、服务、DRA 与 LWS 模板；集群未运行。占位字段必须适配实际环境。
- observability：Prometheus 与 OTLP Collector 配置；需检查实际指标与端点。
- rollouts：受控 CPU 故障服务和分析清单；逻辑测试不等于真实流量回滚验证。

CPU 依赖锁见 requirements.txt 与 locks/cpu-macos-py312.txt。GPU 构建需要匹配设备与驱动，不能照用 macOS 锁文件。记录镜像 digest、模型 revision、输入规模、原始样本及验证状态。未执行项目不要填写示例性能数字。

训练镜像构建：`docker build -f labs/kubernetes/training.Dockerfile -t YOUR_REGISTRY/ai-infra-tiny:VERSION .`。替换仓库和版本后再发布。

清理仅针对本实验创建的资源；先保存证据和检查点。不要删除共享驱动、控制器或他人的命名空间。
