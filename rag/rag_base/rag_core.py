'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-23
  Purpose:
'''

import subprocess
from typing import List, Tuple

from utils.hash_tool import md5sum

from .chunk_tool import IterChunks
from .log_tool import logger
from .rag_base import embed_chunk, summarize_chunk


def prepare_data(
    file_path: str, db_name: str, chunk_size: int = 1000,
    separators: List[str] = None, enable_abstract: bool = True,
    db_client=None):
    """数据准备流程"""
    logger.info(f"Starting data preparation: file={file_path}, db_name={db_name}, chunk_size={chunk_size}, separators={separators}, enable_abstract={enable_abstract}")

    raw_collection = f"{db_name}_raw"
    abstract_collection = f"{db_name}_abstract"

    documents = []
    metadatas = []
    ids = []
    embeddings = []

    abstract_documents = []
    abstract_metadatas = []
    abstract_ids = []
    abstract_embeddings = []

    chunk_count = 0

    # 迭代处理每个分片
    for chunk_text in IterChunks(file_path, chunk_size, separators):
        if not chunk_text.strip():
            continue

        chunk_count += 1

        # 计算MD5作为ID
        chunk_id = md5sum(chunk_text)

        # 向量化知识片段
        chunk_embedding = embed_chunk(chunk_text)

        # 添加到原始知识库
        documents.append(chunk_text)
        metadatas.append({"source": file_path})
        ids.append(chunk_id)
        embeddings.append(chunk_embedding)

        # 生成摘要（如果启用）
        if enable_abstract:
            abstract_text = summarize_chunk(chunk_text)
            abstract_embedding = embed_chunk(abstract_text)

            abstract_documents.append(abstract_text)
            abstract_metadatas.append({"source": file_path, "raw_id": chunk_id})
            abstract_ids.append(chunk_id)
            abstract_embeddings.append(abstract_embedding)

        # （必须）直接添加到数据库，避免占用内存
        if documents:
            db_client.add_documents(raw_collection, documents, metadatas, ids, embeddings)

        if enable_abstract and abstract_documents:
            db_client.add_documents(abstract_collection, abstract_documents, abstract_metadatas, abstract_ids, abstract_embeddings)

        # reset variables
        documents = []
        metadatas = []
        ids = []
        embeddings = []

        abstract_documents = []
        abstract_metadatas = []
        abstract_ids = []
        abstract_embeddings = []

    logger.info(f"Data preparation completed: {file_path}, chunk_count={chunk_count}")
    return {"chunk_count": chunk_count}

def build_prompt(question: str, raw_results: List[Tuple[str, float]],
                    abstract_results: List[Tuple[str, float]]) -> str:
    """构造提示词"""
    prompt = "严格基于以下(信息)回答(问题)，不可以使用你自身的知识库去回答。\n\n信息：\n"

    # 添加原始知识片段
    for i, (doc, _) in enumerate(raw_results, 1):
        prompt += f"{i}) {doc}\n"

    # 添加摘要片段
    start_idx = len(raw_results) + 1
    for i, (doc, _) in enumerate(abstract_results, start_idx):
        prompt += f"{i}) {doc}\n"

    prompt += f"\n问题：{question}"

    return prompt

def call_llm(prompt: str) -> str:
    """调用大模型"""
    try:
        # 调用命令行工具llm_chat
        result = subprocess.run(
            ["llm_chat", prompt],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            msg = f"llm_chat failed: stdout={result.stdout}, stderr={result.stderr}"
            logger.error(msg)
            return msg

    except subprocess.TimeoutExpired:
        logger.error("llm_chat timeout")
        return "抱歉，大模型响应超时"
    except FileNotFoundError:
        logger.error("llm_chat command not found")
        return "抱歉，大模型工具未安装"
    except Exception as e:
        logger.error(f"llm_chat error: {e}")
        return "抱歉，大模型调用出错"
