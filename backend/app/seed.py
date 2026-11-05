from .models import Category

# Initialization data only: the UI always reads the current tree from SQLite.
TREE = {
'机器学习': {'数学基础':['线性代数','概率论与数理统计','微积分','最优化方法'], '传统机器学习':['线性回归','逻辑回归','决策树','支持向量机','集成学习','聚类算法'], '深度学习':['神经网络基础','CNN','RNN','Transformer','注意力机制','优化器','正则化'], '计算机视觉':['图像分类','目标检测','图像分割','视频理解','视频异常检测','多模态视觉感知'], '自然语言处理':['文本表示','词向量','文本分类','序列建模','预训练语言模型'], '大语言模型':['LLM基础','Prompt Engineering','RAG','Function Calling','Agent','MCP','SFT','LoRA','QLoRA','强化学习与对齐'], '模型训练与优化':['模型微调','分布式训练','量化','推理加速'], '模型部署':['Transformers','vLLM','Ollama','LMDeploy'], '模型评估':['分类指标','检测指标','生成式模型评估']},
'前后端': {'前端开发': {'HTML':{},'CSS':{},'JavaScript':['JavaScript基础','ES6+','异步编程','DOM操作'],'TypeScript':{},'Vue':['Vue基础','组件','生命周期','Vue Router','Pinia'],'React':{},'前端工程化':['Vite','npm','Webpack']}, '后端开发': {'Python':['Python基础','面向对象','异步编程','FastAPI','Flask','Django'],'Java':['Java基础','面向对象','JVM','Spring','Spring Boot'],'Go':['Go基础','Gin'],'Node.js':['Node.js基础','Express','NestJS']}, '数据库':['MySQL','PostgreSQL','Redis','SQLite','数据库设计','SQL'], '计算机网络':['TCP/IP','HTTP/HTTPS','TCP与UDP','DNS','网络安全基础'], 'API与接口开发':['RESTful API','请求与响应','身份认证','接口设计'], '部署与工程化':['Linux','Git','Docker','Nginx','CI/CD','项目部署']},
'算法与数据结构': {'基础知识':['时间复杂度','空间复杂度','递归','位运算'], '数据结构':{'数组':{},'字符串':{},'链表':{},'栈':{},'队列':{},'哈希表':{},'树':['二叉树','二叉搜索树','平衡树','堆'],'图':{},'并查集':{},'字典树':{}},'基础算法':['排序','查找','二分查找','双指针','滑动窗口','前缀和'],'进阶算法':['贪心算法','回溯算法','分治算法','动态规划','图论算法','最短路径','拓扑排序'],'题目与练习':['LeetCode','剑指 Offer','面试算法题']}}
def seed(db):
    if db.query(Category).first(): return
    def add(items, parent=None):
        if isinstance(items, list): items = {name: {} for name in items}
        for index, (name, children) in enumerate(items.items()):
            c = Category(name=name, parent_id=parent, sort_order=index, is_system=parent is None)
            db.add(c); db.flush(); add(children, c.id)
    add(TREE); db.commit()
