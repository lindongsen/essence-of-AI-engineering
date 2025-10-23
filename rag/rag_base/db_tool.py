'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose:
'''

import chromadb

from utils.hash_tool import md5sum


class DBClient(object):
    """ database client for embeddings """
    def __init__(self, conn:dict=None):
        """
        :conn:
            @key protocol: temp for EphemeralClient, file for PersistentClient, http ...
            @key path: only for 'file' protocol
            @key host:
            @key port:
        """
        self.client = None
        if not conn or conn.get("protocol") == "temp":
            self.client = chromadb.EphemeralClient()
        elif conn["protocol"] == "file":
            self.client = chromadb.PersistentClient(path=conn["path"])

        assert self.client, f"get db client failed: [{conn}]"

    def get_collection(self, name):
        """ get collection instance """
        return self.client.get_or_create_collection(name=name)

    def get_ids(self, chunks):
        """ get ids for chunks """
        ids = []
        # md5sum
        for chunk in chunks:
            ids.append(md5sum(chunk))
        return ids

    def save_embeddings(self, name, chunks, embeddings, ids=None, metadatas=None):
        """ save data """
        collection = self.get_collection(name)
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids or self.get_ids(chunks),
            metadatas=metadatas,
        )

    def add_documents(self, collection, documents, metadatas, ids, embeddings):
        """ save data to database """
        self.get_collection(collection).add(
            documents=documents,
            metadatas=metadatas,
            ids=ids or self.get_ids(documents),
            embeddings=embeddings,
        )
