'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose:
'''

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder,
)
from transformers import (
    PegasusForConditionalGeneration,
    PegasusTokenizer,
)


# define global variables
g_embedding_model_map = {}
g_cross_encoder_model_map = {}
g_abstract_model_map = {}

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

    print(f"model name: [{model_name}]")

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

    def generate_abstract(self, text:str, model_name:str="google/pegasus-large") -> str:
        """Generate abstract using Pegasus model"""
        pegasus_model, pegasus_tokenizer = get_abstract_model(model_name)
        inputs = pegasus_tokenizer(text, return_tensors="pt", max_length=1024)
        summary_ids = pegasus_model.generate(inputs["input_ids"])
        return pegasus_tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
