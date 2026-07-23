import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from model.factory import embedding_model
from utils.config_handler import chroma_config
from utils.file_handler import (
    get_file_md5_hex,
    listdir_with_allowed_type,
    pdf_loder,
    txt_loder,
)
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self):
        persist_directory = get_abs_path(chroma_config["persist_directory"])
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=embedding_model,
            persist_directory=persist_directory,
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separators"],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})

    def load_document(self):
        def check_md5_hex(md5_for_check: str):
            md5_store_path = get_abs_path(chroma_config["md5_hex_store"])
            if not os.path.exists(md5_store_path):
                open(md5_store_path, "w", encoding="utf-8").close()
                return False

            with open(md5_store_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.strip() == md5_for_check:
                        return True
                return False

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_config["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str):
            if read_path.endswith(".txt"):
                return txt_loder(read_path)

            if read_path.endswith(".pdf"):
                return pdf_loder(read_path)

            return []

        allowed_files_path: tuple[str, ...] = listdir_with_allowed_type(
            get_abs_path(chroma_config["data_path"]),
            tuple(chroma_config["allow_knowledge_file_type"]),
        )
        for path in allowed_files_path:
            md5_hex = get_file_md5_hex(path)
            if not md5_hex:
                logger.warning(f"{path} 无法计算 md5，已跳过")
                continue

            if check_md5_hex(md5_hex):
                logger.info(f"{path} 知识库内容已存在，跳过入库")
                continue

            try:
                documents: list[Document] = get_file_documents(path)
                if not documents:
                    logger.warning(f"{path} 没有有效文本内容")
                    continue

                spliter_document: list[Document] = self.spliter.split_documents(documents)
                if not spliter_document:
                    logger.warning(f"{path} 切片后没有有效内容")
                    continue

                self.vector_store.add_documents(spliter_document)
                save_md5_hex(md5_hex)
                logger.info(f"{path} 加载成功")
            except Exception as e:
                logger.error(f"{path} 加载失败：{str(e)}", exc_info=True)
                continue
