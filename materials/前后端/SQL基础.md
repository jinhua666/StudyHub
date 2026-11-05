---
title: SQL 基础：查询、连接与索引
summary: 通过常见查询理解筛选、连接、聚合及索引的作用。
category: 前后端/数据库/SQL
tags: [SQL, 数据库, SQLite]
status: not_started
difficulty: beginner
---

# SQL 基础：查询、连接与索引

## 查询与筛选

```sql
SELECT id, title, status
FROM notes
WHERE status = 'learning'
ORDER BY updated_at DESC
LIMIT 20;
```

`WHERE` 过滤行，`ORDER BY` 指定顺序，`LIMIT` 限制返回数量。只选择需要的列，有助于减少不必要的数据传输。

## 连接与聚合

```sql
SELECT c.name, COUNT(n.id) AS note_count
FROM categories AS c
LEFT JOIN notes AS n ON n.category_id = c.id
GROUP BY c.id, c.name;
```

`LEFT JOIN` 保留没有文档的分类；这里使用 `COUNT(n.id)`，避免将没有匹配文档的分类计为一篇。外键维护引用关系，但是否自动启用和具体行为取决于数据库配置。

## 索引与安全

为经常筛选或连接的列建立合适索引，可以减少扫描，但也会增加写入与存储成本。使用 SQLite 的 `EXPLAIN QUERY PLAN` 检查具体查询。应用程序中通过参数化查询传入用户输入，避免将输入直接拼接进 SQL。

## 练习

查询每种学习状态下的文档数量，并比较给 `status` 添加索引前后的查询计划。解释为什么索引不是越多越好。
