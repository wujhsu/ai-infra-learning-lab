import {mkdir,writeFile,access} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
const diagrams={
request:`flowchart LR
 C[客户端] --> G[网关与路由] --> E[推理引擎] --> U[GPU 计算]
 U --> E --> C
 K[Kubernetes 控制面] -.资源分配与恢复.-> P[Pod 与设备]
 P -.承载.-> E`,
reconcile:`flowchart LR
 D[声明：需要两个副本] --> A[API Server]
 A --> C[控制器：比较实际状态]
 C --> P[创建 Pod]
 P --> S[调度器：选择节点]
 S --> K[kubelet：启动与探测]
 K -.状态反馈.-> A`,
prefix:`flowchart LR
 R[共同前缀块 1] --> B[共同前缀块 2]
 B --> A[问题 A 的新块] --> OA[回答 A]
 B --> C[问题 B 的新块] --> OB[回答 B]
 X[前缀中段修改] --> Y[后续 K/V 需要重新计算]`,
'cache-tier':`flowchart TD
 R[新请求需要历史 KV] --> Q{可复用？}
 Q -->|否| C[重新计算]
 Q -->|是| B{加载比重算划算？}
 B -->|否| C
 B -->|是| L[从 GPU / DRAM / SSD / 远端加载]
 L --> H{加载成功？}
 H -->|是| D[继续生成]
 H -->|否| F[按预算重试或重算]
 C --> D
 E[会话结束或超时] --> GC[回收不再需要的块]`,
pd:`sequenceDiagram
 participant C as 客户端
 participant R as 路由
 participant P as Prefill 实例
 participant D as Decode 实例
 C->>R: 请求与上下文
 R->>P: 输入计算
 P->>D: KV 交接（数据与布局）
 D-->>R: 交接成功并继续生成
 R-->>C: 流式输出
 Note over P,D: 失败、取消与资源释放必须协调`,
topology:`flowchart TB
 subgraph A[节点 A]
  CA[CPU / NUMA 0] ---|PCIe| GA[GPU 0]
  CA ---|PCIe| NA[NIC]
  GA ---|NVLink：仅支持平台| GA2[GPU 1]
 end
 subgraph B[节点 B]
  CB[CPU / NUMA 0] ---|PCIe| GB[GPU 0]
  CB ---|PCIe| NB[NIC]
  GB ---|NVLink：仅支持平台| GB2[GPU 1]
 end
 NA <-->|跨节点网络| NB`,
preflight:`flowchart TD
 A[所有 rank 启动 init 检查] --> B[设备 / 挂载 / 配置]
 B --> C[对端发现 / DNS / 网络]
 C --> D[全组 collective]
 D --> E{所有 rank 通过？}
 E -->|是| F[加载模型并验证服务]
 E -->|否| G[保存 rank 与节点证据]
 G --> H{重试预算内且可恢复？}
 H -->|是| A
 H -->|否| S[停止或隔离后重新调度]`,
correlation:`flowchart LR
 T[请求 Trace ID] --> S[网关 / 引擎 Span]
 S --> P[实例与 Pod UID]
 P --> N[节点与 GPU UUID]
 N --> M[设备指标时间窗口]
 S --> W[排队 / Prefill / 输出阶段]
 M -.辅助判断，非精确请求归因.-> W`,
rollout:`flowchart TD
 V[候选版本] --> C[小比例流量]
 C --> A[分析：样本 / 延迟 / 错误]
 A --> R{结果}
 R -->|成功| N[逐步放量]
 R -->|失败| B[停止新流量并回滚]
 R -->|无数据或不确定| P[暂停与补充证据]
 B --> F[修复 PR]
 F --> T[评审与测试] --> V`,
capstone:`flowchart LR
 A[单服务基线] --> B[多卡通信]
 B --> C[多节点模型]
 C --> D[LWS 与设备分配]
 D --> E[观测与故障诊断]
 E --> F[Canary 与恢复]
 A -.保留测量.-> R[配置 / 原始样本 / 复盘]
 D -.保留事件.-> R
 F -.保留回滚证据.-> R`,
'agent-loop':`flowchart LR
 P[计划与硬件假设] --> C[实现候选]
 C --> T{正确性通过？}
 T -->|否| L[记录失败]
 T -->|是| B[重复测量与 Profile]
 B --> A[解释瓶颈]
 A --> P
 L --> P`,
'dra-topology':`flowchart LR
 G[GPU driver 属性] --> N[统一 NUMA 语义]
 I[NIC driver 属性] --> N
 N --> M[Claim 共置约束]
 M --> S[调度与分配]
 S --> P[驱动准备]
 P --> W[工作负载]
`,
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
