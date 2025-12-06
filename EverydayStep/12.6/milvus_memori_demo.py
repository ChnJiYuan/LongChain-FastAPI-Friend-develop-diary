"""
milvus_memori_demo.py

一个极简 demo：展示「Memori（结构化记忆）+ Milvus（向量检索）」的组合用法。

- MockMemoriClient：模拟一个简单的 Memori 客户端
- Milvus 向量库：存用户的原始对话文本，支持相似度检索
- MemoryService：对外提供 save_message / retrieve_context 两个方法
"""

from typing import List, Dict, Any
from dataclasses import dataclass

# --------- 1. Mock Memori 部分（你之后可以替换成真实 Memori SDK） ---------


class MockMemoriClient:
    """
    简化版 Memori：
    - 按 user_id 存储“事实列表”
    - query 时简单返回最近的几条
    真实项目里，你可以改成调用 Memori SDK 的 save/query 方法。
    """

    def __init__(self):
        # { user_id: [fact1, fact2, ...] }
        self._store: Dict[str, List[str]] = {}

    def save(self, user_id: str, content: str):
        """保存一条“事实”或对话内容。真实场景下，这里可以先做信息抽取再存。"""
        self._store.setdefault(user_id, []).append(content)

    def query(self, user_id: str, query_text: str, limit: int = 5) -> List[str]:
        """
        简单实现：不做语义搜索，只返回最近几条。
        真实 Memori 一般会做结构化抽取 + 语义检索。
        """
        history = self._store.get(user_id, [])
        return history[-limit:]


# --------- 2. Milvus 部分：向量存储 ---------

from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)

from sentence_transformers import SentenceTransformer


def init_milvus_collection(
    collection_name: str = "chat_history", dim: int = 384
) -> Collection:
    """连接 Milvus，如果不存在指定 collection 就自动创建。"""
    connections.connect("default", host="localhost", port="19530")

    if not utility.has_collection(collection_name):
        print(f"[Milvus] Creating collection: {collection_name}")

        fields = [
            FieldSchema(
                name="pk",
                dtype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            ),
            FieldSchema(
                name="user_id",
                dtype=DataType.VARCHAR,
                max_length=64,
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=2048,
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=dim,
            ),
        ]
        schema = CollectionSchema(fields, description="Chat history embeddings")
        collection = Collection(name=collection_name, schema=schema)

        # 创建向量索引
        index_params = {
            "metric_type": "IP",          # 内积，相当于余弦相似可用
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
    else:
        print(f"[Milvus] Using existing collection: {collection_name}")
        collection = Collection(collection_name)

    # 加载到内存
    collection.load()
    return collection


# --------- 3. MemoryService：组合 Memori + Milvus ---------


@dataclass
class RetrievedContext:
    memori_facts: List[str]
    milvus_snippets: List[str]


class MemoryService:
    """
    统一对外的记忆服务：
    - save_message(user_id, message)：写入 Memori & Milvus
    - retrieve_context(user_id, query)：从 Memori & Milvus 同时取相关内容
    """

    def __init__(self, memori_client: MockMemoriClient, milvus_collection: Collection):
        self.memori = memori_client
        self.collection = milvus_collection
        # 这里用一个轻量的 embedding 模型，你之后也可以换成 OpenAI embedding
        self.emb_model = SentenceTransformer("all-MiniLM-L6-v2")

    # ---- 内部工具方法 ----

    def _embed(self, text: str) -> List[float]:
        vec = self.emb_model.encode(text)
        return vec.tolist()

    # ---- 对外接口 ----

    def save_message(self, user_id: str, message: str):
        """
        一条新消息进来时：
        1. 写入 Memori（结构化记忆）
        2. 写入 Milvus（向量检索用）
        """
        # 1) Memori 保存（可以理解为“抽取事实 + 存储”）
        self.memori.save(user_id, message)

        # 2) Milvus 写入
        embedding = self._embed(message)
        data = [
            [user_id],        # user_id 列
            [message],        # text 列
            [embedding],      # embedding 列
        ]
        # 注意：pk 是 auto_id=True，不需要手动传
        self.collection.insert(data)
        self.collection.flush()
        print(f"[MemoryService] Saved message for user {user_id} to Memori + Milvus.")

    def retrieve_context(
        self, user_id: str, query: str, top_k: int = 3
    ) -> RetrievedContext:
        """
        生成回复前，从两个记忆层取出“与当前 query 相关”的信息。
        """

        # 1) 从 Memori 取最近的“事实”
        memori_facts = self.memori.query(user_id, query, limit=top_k)

        # 2) 从 Milvus 做向量检索
        query_vec = self._embed(query)
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10},
        }
        # expr 里限定 user_id，这样每个用户的记录互不干扰
        expr = f'user_id == "{user_id}"'
        results = self.collection.search(
            data=[query_vec],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["text", "user_id"],
        )

        milvus_snippets: List[str] = []
        if results and len(results) > 0:
            hits = results[0]
            for hit in hits:
                milvus_snippets.append(hit.entity.get("text"))

        return RetrievedContext(
            memori_facts=memori_facts,
            milvus_snippets=milvus_snippets,
        )


# --------- 4. Demo 运行逻辑 ---------


def run_demo():
    # 1) 初始化 MockMemori + Milvus
    memori_client = MockMemoriClient()
    collection = init_milvus_collection(collection_name="chat_history_demo", dim=384)
    memory_service = MemoryService(memori_client, collection)

    user_id = "user_001"

    # 2) 模拟用户过去几轮对话
    history_messages = [
        "我最近在实习，主要做的是小红书的文案和数据分析。",
        "我在自学 LangChain 和 FastAPI，想做一个陪伴型聊天助手。",
        "我最近皮肤有点敏感，长了很多痘痘，还在看医生。",
        "我打算寒假好好学一下 AI + 游戏开发，想试试用 UE5 做 Demo。",
    ]

    for msg in history_messages:
        memory_service.save_message(user_id, msg)

    # 3) 现在来一条“当前问题”，看看系统怎么检索上下文
    current_query = "我那个陪伴聊天助手的项目，你还记得是用什么技术栈吗？"

    ctx = memory_service.retrieve_context(user_id, current_query, top_k=3)

    print("\n====== Memori 返回的“结构化事实”（最近几条）======")
    for i, fact in enumerate(ctx.memori_facts, 1):
        print(f"{i}. {fact}")

    print("\n====== Milvus 返回的“相似历史对话片段” ======")
    for i, snippet in enumerate(ctx.milvus_snippets, 1):
        print(f"{i}. {snippet}")

    # 4) 这一步在真实项目里会交给 LLM 生成最终回答
    # 这里我们只是打印出可以用来构造 prompt 的上下文
    print("\n====== 可用于 LLM Prompt 的综合上下文示意 ======")
    full_context = (
        "【关于用户的长期信息（Memori）】\n"
        + "\n".join(ctx.memori_facts)
        + "\n\n【与当前问题最相似的历史记录（Milvus）】\n"
        + "\n".join(ctx.milvus_snippets)
    )
    print(full_context)


if __name__ == "__main__":
    run_demo()
