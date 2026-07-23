import hashlib
import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

try:
    from .logger_handler import logger
except ImportError:
    from logger_handler import logger


def get_file_md5_hex(filepath: str):
    if not os.path.exists(filepath):
        logger.error(f"[md5] 文件不存在：{filepath}")
        return None
    if not os.path.isfile(filepath):
        logger.error(f"[md5] 路径不是文件：{filepath}")
        return None

    md5_obj = hashlib.md5()
    chunk_size = 4096
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)

        return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"计算 {filepath} md5 失败：{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str, ...]):
    files = []
    if not os.path.isdir(path):
        logger.warning(f"[listdir_with_allowed_type] 目录不存在：{path}")
        return tuple()

    normalized_types = tuple(
        file_type if file_type.startswith(".") else f".{file_type}"
        for file_type in allowed_types
    )
    for filename in os.listdir(path):
        if filename.endswith(normalized_types):
            files.append(os.path.join(path, filename))

    return tuple(files)


def pdf_loder(filepath: str, password=None) -> list[Document]:
    return PyPDFLoader(filepath, password).load()


def txt_loder(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()
