# Agent Markdown 导入格式

UTF-8 Markdown 文件可使用 YAML Front Matter。`category` 是从一级板块开始、以 `/` 分隔的完整路径；导入预览中可选择自动创建缺失的子分类。一级板块必须已经存在。

```markdown
---
id: 12 # 可选；仅在希望匹配已有文档时填写
title: Transformer 注意力机制
summary: 注意力机制的基本原理
category: 机器学习/深度学习/Transformer
tags: [Transformer, Attention]
status: not_started
difficulty: intermediate
source_url: https://example.com
---

# Transformer 注意力机制

正文保留原始 Markdown。
```

状态可选 `not_started`、`learning`、`mastered`；难度可选 `beginner`、`intermediate`、`advanced`。不填 ID 会创建新文档；ID 已存在时按导入选项跳过或更新。分类路径优先精确匹配现有完整路径；名称中含 `/` 可能造成路径歧义，请尽量避免重名路径，必要时通过 API 使用分类 ID 写入。批量导入只处理 Markdown 文本，关联附件请另行上传。
