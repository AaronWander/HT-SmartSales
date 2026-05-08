# Presales RAG 文档索引

这个目录集中存放 Hermes 中“售前服务目录 + RAGFlow + 槽位对齐 + 模板方案输出 + 阶段状态机”相关文档，避免文档散落在 `plans/`、临时目录或对话记录里。

## 当前文档

1. [设计流程架构与决策记录](./design-decision-record.md)
   当前 presales 业务层的总体设计、状态机、服务目录结构、代码落点、测试记录。
2. [运行时配置与文件位置](./runtime-config.md)
   说明服务目录、`proposal.md`、`slots.yaml` 放在哪里，修改后如何生效。
3. [模板变量与撰写规范](./TEMPLATE_GUIDE.md)
   说明 `slot/sys/rag/ai/ext` 五类变量的写法、边界和模板撰写建议。

## 当前业务文件位置

业务配置不写在文档目录里，实际由服务目录驱动：

```text
presales_services/
  客户专属穿搭服务/
    proposal.md
    slots.yaml
```

## 文档保留原则

1. 架构设计与决策变化，更新 `design-decision-record.md`。
2. 用户需要知道“文件放哪里、怎么改、怎么重启”，更新 `runtime-config.md`。
3. 模板变量、占位符和模板写作规则，更新 `TEMPLATE_GUIDE.md`。
4. 不再新增临时散文档；如果是短期计划，放到 `plans/` 或任务记录里，不放进本目录。
