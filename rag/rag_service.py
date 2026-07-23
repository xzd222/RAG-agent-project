from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from model.factory import chat_model
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts


class RagSummarizeService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self):
        return self.prompt_template | self.model | StrOutputParser()

    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)

        if not context_docs:
            return "知识库中没有检索到相关资料，暂时无法基于本地知识库回答该问题。"

        context = "\n".join(
            f"[参考资料{index}] {doc.page_content} | 元数据: {doc.metadata}"
            for index, doc in enumerate(context_docs, start=1)
        )

        return self.chain.invoke({
            "input": query,
            "context": context,
        })


if __name__ == "__main__":
    rag = RagSummarizeService()
    print(rag.rag_summarize("123"))
