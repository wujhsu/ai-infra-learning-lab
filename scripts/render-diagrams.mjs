import {mkdir,writeFile,access} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
const diagrams={
  "admission": "flowchart TB\n J[训练 Job：完整资源需求] --> L[LocalQueue：提交入口]\n L --> C[ClusterQueue：预算与策略]\n C --> A[Workload 获得准入]\n A --> S[调度器：节点放置]\n S --> D[设备分配与节点准备]\n D --> T[首次有效训练 step]\n T --> R[完成或恢复后释放预算]",
  "agent-loop": "flowchart LR\n P[计划与硬件假设] --> C[实现候选]\n C --> T{正确性通过？}\n T -->|否| L[记录失败]\n T -->|是| B[重复测量与 Profile]\n B --> A[解释瓶颈]\n A --> P\n L --> P",
  "compile": "flowchart TB\n P[Python 函数与张量输入] --> C[捕获可处理的计算图]\n C --> G[守卫：输入条件是否适用]\n G -->|匹配| R[复用已编译结果]\n G -->|不匹配| B[重新捕获或编译]\n C --> I[后端优化与代码生成]\n I --> R\n B --> I\n R --> E[设备执行]\n C -.图断点.-> F[普通执行片段]",
  "correlation": "flowchart LR\n T[请求 Trace ID] --> S[网关 / 引擎 Span]\n S --> P[实例与 Pod UID]\n P --> N[节点与 GPU UUID]\n N --> M[设备指标时间窗口]\n S --> W[排队 / Prefill / 输出阶段]\n M -.辅助判断，非精确请求归因.-> W",
  "ddp": "flowchart TB\n subgraph A[rank 0]\n  L0[本地样本与损失] --> B0[反向：梯度逐组就绪]\n end\n subgraph B[rank 1]\n  L1[另一份样本与损失] --> B1[反向：梯度逐组就绪]\n end\n B0 --> C[同步对应梯度组]\n B1 --> C\n C --> U0[rank 0：相同更新规则]\n C --> U1[rank 1：相同更新规则]\n U0 --> W0[一致参数]\n U1 --> W1[一致参数]",
  "dra-flow": "flowchart TB\n DR[设备驱动] --> I[ResourceSlice：库存]\n CL[DeviceClass：类别规则] --> S[调度与分配]\n RC[ResourceClaim：请求] --> S\n I --> S\n P[Pod：引用声明] --> S\n S --> A[Claim 分配结果]\n A --> K[kubelet 与节点驱动准备]\n K --> C[容器使用设备]\n C --> U[清理与声明生命周期]\n U --> I",
  "dra-topology": "flowchart LR\n G[GPU driver 属性] --> N[统一 NUMA 语义]\n I[NIC driver 属性] --> N\n N --> M[Claim 共置约束]\n M --> S[调度与分配]\n S --> P[驱动准备]\n P --> W[工作负载]\n",
  "engine": "flowchart TB\n R[请求与输入 token] --> Q[等待队列]\n Q --> S[调度：本轮计算预算]\n S <-->|分配与引用| K[KV 块管理]\n S --> E[模型执行：输入或新位置]\n E --> O[候选得分与采样]\n O --> D{结束或取消？}\n D -->|否| S\n D -->|是| F[完成状态与释放活动引用]\n O --> C[流式输出]",
  "kv-pages": "flowchart TB\n A[请求 A：逻辑块 0 / 1 / 2] --> T[块表：逻辑位置到物理块]\n B[请求 B：逻辑块 0 / 1] --> T\n T --> P0[物理块 7：共享前缀]\n T --> P1[物理块 2：A 后续]\n T --> P2[物理块 9：B 后续]\n F[空闲或可淘汰块池] --> T\n P1 -->|引用释放后可回收| F",
  "measure": "flowchart LR\n A[固定环境与输入] --> B[验证数值正确]\n B --> C[首次编译与预热单列]\n C --> D[同步边界与重复计时]\n D --> E[保存样本与误差]\n E --> F[Profile 定位瓶颈]\n F --> G[一次改变一个机制]\n G --> B",
  "memory": "flowchart TB\n CPU[CPU：准备输入与提交计算] -->|主机到设备搬运| HBM[显存：权重 / 激活 / KV]\n HBM -->|读取数据| SM[GPU 执行单元]\n SM --> SH[片上共享内存与寄存器]\n SH --> SM\n SM -->|写回结果| HBM\n HBM -->|必要结果回传| CPU",
  "pd": "sequenceDiagram\n participant C as 客户端\n participant R as 路由\n participant P as Prefill 实例\n participant D as Decode 实例\n C->>R: 请求与上下文\n R->>P: 输入计算\n P->>D: KV 交接（数据与布局）\n D-->>R: 交接成功并继续生成\n R-->>C: 流式输出\n Note over P,D: 失败、取消与资源释放必须协调",
  "prefix": "flowchart LR\n R[共同前缀块 1] --> B[共同前缀块 2]\n B --> A[问题 A 的新块] --> OA[回答 A]\n B --> C[问题 B 的新块] --> OB[回答 B]\n X[前缀中段修改] --> Y[后续 K/V 需要重新计算]",
  "preflight": "flowchart TD\n A[所有 rank 启动 init 检查] --> B[设备 / 挂载 / 配置]\n B --> C[对端发现 / DNS / 网络]\n C --> D[全组 collective]\n D --> E{所有 rank 通过？}\n E -->|是| F[加载模型并验证服务]\n E -->|否| G[保存 rank 与节点证据]\n G --> H{重试预算内且可恢复？}\n H -->|是| A\n H -->|否| S[停止或隔离后重新调度]",
  "reconcile": "flowchart LR\n D[声明：需要两个副本] --> A[API Server]\n A --> C[控制器：比较实际状态]\n C --> P[创建 Pod]\n P --> S[调度器：选择节点]\n S --> K[kubelet：启动与探测]\n K -.状态反馈.-> A",
  "rollout": "flowchart TD\n V[候选版本] --> C[小比例流量]\n C --> A[分析：样本 / 延迟 / 错误]\n A --> R{结果}\n R -->|成功| N[逐步放量]\n R -->|失败| B[停止新流量并回滚]\n R -->|无数据或不确定| P[暂停与补充证据]\n B --> F[修复 PR]\n F --> T[评审与测试] --> V",
  "topology": "flowchart TB\n subgraph A[节点 A]\n  CA[CPU / NUMA 0] ---|PCIe| GA[GPU 0]\n  CA ---|PCIe| NA[NIC]\n  GA ---|NVLink：仅支持平台| GA2[GPU 1]\n end\n subgraph B[节点 B]\n  CB[CPU / NUMA 0] ---|PCIe| GB[GPU 0]\n  CB ---|PCIe| NB[NIC]\n  GB ---|NVLink：仅支持平台| GB2[GPU 1]\n end\n NA <-->|跨节点网络| NB"
};
await mkdir('public/diagrams',{recursive:true});await mkdir('.astro/diagrams',{recursive:true});
const browser=process.env.PUPPETEER_EXECUTABLE_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
await access(browser);
await writeFile('.astro/diagrams/puppeteer.json',JSON.stringify({executablePath:browser,args:['--no-sandbox']}));
await writeFile('.astro/diagrams/theme.json',JSON.stringify({theme:'base',themeVariables:{fontFamily:'PingFang SC, Microsoft YaHei, sans-serif',fontSize:'17px',primaryColor:'#e7f0fa',primaryTextColor:'#17304c',primaryBorderColor:'#6b91b7',lineColor:'#62809d',secondaryColor:'#e1f3ec',tertiaryColor:'#fff0d4'},flowchart:{curve:'basis',htmlLabels:false}}));
for(const[id,source]of Object.entries(diagrams)){
 await writeFile(`.astro/diagrams/${id}.mmd`,source);
 execFileSync('node_modules/.bin/mmdc',['-i',`.astro/diagrams/${id}.mmd`,'-o',`public/diagrams/${id}.svg`,'-b','white','-c','.astro/diagrams/theme.json','-p','.astro/diagrams/puppeteer.json'],{stdio:'pipe'});
 await writeFile(`public/diagrams/${id}.mmd`,source);
}console.log(`Rendered ${Object.keys(diagrams).length} diagrams`);
