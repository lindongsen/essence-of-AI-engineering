'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose:
'''

import re

#import nltk
#nltk.download('punkt')
#nltk.download('punkt_tab')
#from nltk.tokenize import sent_tokenize

import torch
from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder,
)
from transformers import (
    PegasusForConditionalGeneration,
    PegasusTokenizer,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


# define global variables
g_embedding_model_map = {}
g_cross_encoder_model_map = {}
g_abstract_model_map = {}

def split_sentence(text:str):
    """ return sentences """
    #sentences = sent_tokenize(text)
    sentences = re.split(r'(?<=[。！？.!?])', text)
    return sentences

def get_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """ return a instance of SentenceTransformer.

    ref: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    """
    if model_name in g_embedding_model_map:
        return g_embedding_model_map[model_name]

    embedding_model = SentenceTransformer(model_name)
    g_embedding_model_map[model_name] = embedding_model
    return embedding_model

def get_cross_encoder(model_name="cross-encoder/ms-marco-MiniLM-L6-v2"):
    """ return a instance of CrossEncoder.

    ref: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2
    """
    if model_name in g_cross_encoder_model_map:
        return g_cross_encoder_model_map[model_name]

    cross_encoder = CrossEncoder(model_name)
    g_cross_encoder_model_map[model_name] = cross_encoder
    return cross_encoder

def get_abstract_model(model_name="google/pegasus-large"):
    """ return 2 instances, (model, tokenizer) """
    if model_name in g_abstract_model_map:
        return g_abstract_model_map[model_name]

    print(f"loading model: [{model_name}]")

    pegasus_tokenizer = PegasusTokenizer.from_pretrained(model_name)
    pegasus_model = PegasusForConditionalGeneration.from_pretrained(model_name)
    g_abstract_model_map[model_name] = (pegasus_model, pegasus_tokenizer)
    return g_abstract_model_map[model_name]


class IterChunks(object):
    """ iter string for chunk """
    def __init__(self, file_path):
        self.file_path = file_path
        self.fd = open(file_path)
        return

    def __del__(self):
        try:
            self.fd.close()
        except Exception as _:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        return self.get_chunk()

    def get_chunk(self):
        """ return string for chunk """
        s = self.fd.readline()
        if not s:
            self.fd.close()
            raise StopIteration

        while True:
            line = self.fd.readline()
            if not line:
                break

            s += line
            if line.strip() == "":
                break
        return s

def embed_chunk(chunk: str) -> list[float]:
    """ return list of embeddings """
    model = get_embedding_model()
    embeddings = model.encode(chunk)
    return embeddings


class Summarizer(object):
    """ abstract class """
    def __init__(self, model_name="eboafour1/bertsum", top_k=5):
        """初始化模型和tokenizer"""
        model = None
        tokenizer = None
        if model_name in g_abstract_model_map:
            model, tokenizer = g_abstract_model_map[model_name]
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            g_abstract_model_map[model_name] = (model, tokenizer)

        self.tokenizer = tokenizer
        self.model = model
        self.model.eval()

        self.top_k = top_k or 5

    def preprocess_text(self, text):
        """预处理文本，使用更精确的句子分割"""
        return split_sentence(text)

    def score_sentences(self, sentences):
        """对句子进行评分"""
        scores = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 5:  # 跳过过短的句子
                scores.append(0)
                continue

            try:
                inputs = self.tokenizer(
                    sentence,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True,
                    padding=True
                )

                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # 使用模型输出的置信度作为评分
                    score = torch.softmax(outputs.logits, dim=-1).max().item()
                    scores.append(score)
            except Exception as e:
                print(f"处理句子时出错: {e}")
                scores.append(0)

        return scores

    def extractive_summarize(self, text, ratio=0.3, top_k=5):
        """ 抽取式摘要

        Args:
            text: 输入文本
            ratio: 摘要长度占原文的比例
        """
        sentences = self.preprocess_text(text)

        # debug
        #print(f"sentences={sentences}, len={len(sentences)}, top_k={top_k}")

        if len(sentences) <= 3:
            return text  # 如果句子数很少，返回原文

        # 对句子评分
        scores = self.score_sentences(sentences)

        # 计算要选择的句子数
        target_count = max(2, min(top_k, int(len(sentences) * ratio)))

        # 选择评分最高的句子
        ranked = sorted(zip(sentences, scores), key=lambda x: x[1], reverse=True)
        top_sentences = [s for s, _ in ranked[:target_count]]

        # debug
        #print(f"ranked={ranked}, scores={scores}, count={target_count}")

        # 按原文顺序重新排列
        final_summary = []
        for sentence in sentences:
            if sentence in top_sentences:
                final_summary.append(sentence)

        return "。".join(final_summary) + "。"

    def summarize(self, text, method="extractive", ratio=0.3):
        """
        文本摘要主函数

        Args:
            text: 输入文本
            method: 摘要方法
            ratio: 摘要比例

        Returns:
            str: 摘要文本
        """
        if method == "extractive":
            return self.extractive_summarize(text, ratio, self.top_k)
        else:
            raise ValueError("目前只支持extractive方法")


class RAGCtler(object):
    """ controller for RAG """
    def __init__(self, db):
        self.db = db

    def retrieve(self, query: str, index_name:str, top_k: int) -> list[str]:
        """
        :query: the user question;
        :index_name: the database name;
        """
        query_embedding = embed_chunk(query)
        results = self.db.get_collection(index_name).query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results['documents'][0]

    def rerank(self, query: str, chunks: list[str], top_k: int) -> list[str]:
        """
        :query: the user question;
        :chunks: the chunks were retrieved, get them from embedding database.
        """
        cross_encoder = get_cross_encoder()
        pairs = [(query, chunk) for chunk in chunks]
        scores = cross_encoder.predict(pairs)
        if scores is None or len(scores) == 0:
            return None

        index_score_list = list(zip(range(len(scores)), scores))
        index_score_list.sort(key=lambda x: x[1], reverse=True)
        count = 0
        new_chunks = []
        for index, _ in index_score_list:
            new_chunks.append(chunks[index])
            count += 1
            if count >= top_k:
                break
        return new_chunks

    def generate_abstract(self, text:str, model_name:str="google/pegasus-large", top_k=5) -> str:
        """Generate abstract using Pegasus model"""
        flag_use_summarizer = False
        if 'bertsum' in model_name:
            flag_use_summarizer = True

        if flag_use_summarizer:
            return Summarizer(model_name, top_k).summarize(text)

        pegasus_model, pegasus_tokenizer = get_abstract_model(model_name)
        inputs = pegasus_tokenizer(text, return_tensors="pt", max_length=1024)
        summary_ids = pegasus_model.generate(inputs["input_ids"])
        return pegasus_tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
