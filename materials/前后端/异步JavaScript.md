---
title: JavaScript 异步编程：Promise 与 async/await
summary: 理解 Promise 状态、异步错误处理以及并发与串行执行。
category: 前后端/前端开发/JavaScript/异步编程
tags: [JavaScript, Promise, 异步编程]
status: not_started
difficulty: beginner
---

# JavaScript 异步编程：Promise 与 async/await

## Promise

Promise 表示一个异步操作的最终结果，状态从 pending 变为 fulfilled 或 rejected，完成后不再改变。`then` 处理成功结果，`catch` 处理拒绝，`finally` 可执行清理逻辑。

```js
async function getNote(id) {
  const response = await fetch(`/api/notes/${id}`)
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

try {
  const note = await getNote(1)
  console.log(note.title)
} catch (error) {
  console.error('读取失败', error)
}
```

`fetch` 遇到网络错误会拒绝 Promise，但 HTTP 404 或 500 通常仍会得到 Response，因此需要检查 `response.ok`。

## 串行与并发

如果第二个操作依赖第一个结果，应依次 `await`。如果多个操作相互独立，可以先创建 Promise 再使用 `Promise.all` 等待；其中任一失败会使整体拒绝。希望收集每个操作的成功或失败结果时，可使用 `Promise.allSettled`。

## 练习

并发请求三篇知识文档；分别使用 `Promise.all` 和 `Promise.allSettled`，观察其中一个请求失败时的结果。尝试用 `AbortController` 取消不再需要的请求。
