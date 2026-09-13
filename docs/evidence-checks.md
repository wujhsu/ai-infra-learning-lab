# 核验清单 · 2026-09-13

可达性检查数据见 `src/data/source-checks.json`。HTTP 200 只能证明能访问，不代替以下技术核对；滚动文档将来可能变化。

| 核对点 | 依据 | 处理方式 |
|---|---|---|
| vLLM 实验基线 | 官方 v0.29.0 发布 | 镜像固定标签，拉取后记录 digest；模型独立解析 40 位 commit |
| 多节点 MP 参数 | v0.29.0 arg_utils.py 与 Parallelism and Scaling | 检查 nnodes、node-rank、master-addr、master-port；显式 MP backend |
| Prefix Cache 复用边界 | vLLM Automatic Prefix Caching | 复用前缀计算，不消除每个新 token 的 Decode |
| PD 分离状态 | vLLM Disaggregated Prefilling | 说明实验性/connector 依赖与传输成本，不承诺自动加速 |
| NCCL 基础与 Device API | NVIDIA NCCL 2.31.2 文档 | 主机 API、设备侧通信与内存可见性分开；PyTorch 内嵌 NCCL 需另查 |
| DRA 能力成熟度 | Kubernetes DRA works / features | ResourceSlice 库存、ResourceClaim 分配、kubelet 准备分开；逐特性核对开关 |
| LWS 字段 | v0.10.0 leaderworkerset_types.go | size、startupPolicy、restartPolicy、环境变量从版本源码核对 |
| LWS Preflight | 上游提案、会议材料 | 明确教学门禁与完整提案实现不同，不编造已发布字段 |
| 流式时间 | 讲义 observability 第 11 页 + SSE 客户端 | 忽略空 role 事件；首内容不等于精确首 token；截断流记失败 |
| 信号语义 | OpenTelemetry Signals | Metrics / Logs / Traces 各自用途；关联不等于自动建立因果关系 |
| 分位数聚合 | Prometheus 官方 histogram 文档 | 不平均实例 p95，说明样本与统计口径 |
| 发布控制 | Argo Rollouts 1.10.0 / Analysis | Canary 控制版本与路由，LWS 控制工作组；无路由集成不声称精确流量权重 |

文档迁移：vLLM distributed_serving 旧入口改为 serving/parallelism_scaling；OpenTelemetry Signals 使用 docs/concepts/signals。OpenTelemetry 的一次 Node HTTP 检查超时，随后通过官方页面读取确认可用，保留原检查结果以免混淆执行记录。

待真实环境验证：GPU 镜像启动、驱动兼容性、跨节点通信、DRA 驱动属性与准备路径、LWS 组恢复、Argo 分析状态和回滚后业务行为。教材给出命令、检查点和清理路径；结果必须由实际执行补全。
