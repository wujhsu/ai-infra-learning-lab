# 证据与核验

核验日期：2026-09-13。通用数学机制与版本行为分开。来源清单在 src/data/sources.json，正文在相关主张处提供官方链接；详细来源折叠展示。

- PyTorch v2.14.0：Linear、DDP、FSDP2 与 Dynamo 入口源码已读取；CPU autograd/训练/DDP/DCP 实际执行。
- vLLM v0.29.0：EngineCore.step、Scheduler.schedule、KVCacheManager.allocate_slots 已读取。GPU 服务和性能未运行。
- Kubernetes v1.36.0：DRA Filter/Reserve/PreBind 与 kubelet PrepareResources/UnprepareResources 已读取。集群路径未运行。
- Qwen3-0.6B revision c1899de289a04d12100db370d81485cdf75e47ca：官方模型身份核对；真实分词与模型输出需项目环境执行。
- 官方滚动资料用于核对当前支持与机制，不作为可复现依赖锁。特定高级功能需同时核对 API、功能门、驱动及硬件。

214 页讲义索引与 12 场资料保留。精选机制页有原文件、页码、预览/高清路径。NCCL 24、可观测性 11、DRA 23 用于正文证据，其余精选页可从场次索引查阅。会议材料可全部移除而不破坏教学链。完整妙记和个人元数据不进入公开构建。

手工数字与随机初始化/训练结果明确区分。图解与 TypeScript 计算共享 toy-model.json；真实小模型使用独立、明确说明的 32 维两层架构。小模型成绩不是 Qwen 或生产性能结论。

待硬件核验：LoRA BF16、Triton/NCCL/FSDP、量化与推测、实际取消回收、DRA/LWS/Kueue、真实路由回滚。研究专题仅提供机制与对照设计，不冒充已运行。
