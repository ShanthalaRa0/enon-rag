from services.embedding_service import EmbeddingService
from services.reranking_service import RerankingService


def get_embedding_service():

    return EmbeddingService()


def get_reranking_service():

    return RerankingService()