from abc import ABC, abstractmethod
from typing import Optional

from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import BaseChatModel, ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings

from utils.config_handler import agent_config


load_dotenv()


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=agent_config["chat_model_name"])


class EmbeddingFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=agent_config["embedding_model_name"])


chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingFactory().generator()
