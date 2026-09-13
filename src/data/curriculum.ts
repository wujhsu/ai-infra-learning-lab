export const modules = [
 {title:'看见整个系统',subtitle:'把一个请求放回它经过的每一层',color:'blue'},
 {title:'让模型跑起来',subtitle:'从硬件与代码走到第一个服务',color:'teal'},
 {title:'理解快与慢',subtitle:'时间、显存和并发之间的取舍',color:'orange'},
 {title:'让上下文被复用',subtitle:'缓存与 Agent 的长生命周期',color:'purple'},
 {title:'让 GPU 协作',subtitle:'数据如何切分、传输与同步',color:'blue'},
 {title:'把系统部署起来',subtitle:'设备、拓扑和工作组的生命周期',color:'teal'},
 {title:'沿着证据排障',subtitle:'从用户感受追到实际瓶颈',color:'orange'},
 {title:'可靠地交付变更',subtitle:'验证、回滚、修复与完整实践',color:'purple'},
];
export const titles = [
 ['01-request','一个请求，怎样到达 GPU？'],['02-kubernetes','谁在运行服务，谁在管理服务？'],['03-attention','模型怎样利用前面的文字？'],
 ['04-hardware','GPU 的时间花在计算，还是搬数据？'],['05-pytorch','一行 PyTorch 怎样变成 GPU 工作？'],['06-vllm','部署第一个可以测量的推理服务'],
 ['07-latency','为什么首个 token 很慢？'],['08-batching','更多请求，怎样一起执行？'],['09-kv-memory','KV Cache 为什么会吃满显存？'],
 ['10-prefix','相同的开头，能省掉多少计算？'],['11-tiered-cache','缓存放在哪里，才真的划算？'],['12-disaggregation','为什么把 Prefill 和 Decode 分开？'],
 ['13-parallelism','模型和请求，应该怎样分给多张卡？'],['14-collectives','多张 GPU 怎样交换结果？'],['15-nccl','让通信和计算同时推进'],
 ['16-gpu-scheduling','Kubernetes 怎样给 Pod 找到 GPU？'],['17-dra','一次设备请求经历了什么？'],['18-lws','为什么 Pod Running 还不够？'],
 ['19-signals','指标、日志和追踪各回答什么？'],['20-correlation','怎样从慢请求追到 GPU？'],['21-diagnosis','把三个性能故障查清楚'],
 ['22-canary','怎样让坏版本少影响一些用户？'],['23-agent-repair','Agent 能参与修复到哪一步？'],['24-capstone','交付一个可观测、可恢复的推理系统'],
] as const;
export const lessonUrl=(id:string)=>`${import.meta.env.BASE_URL}learn/${id}/`;
export const asset=(path:string)=>`${import.meta.env.BASE_URL}${path.replace(/^\//,'')}`;
