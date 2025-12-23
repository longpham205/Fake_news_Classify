# backend/models/news_inferencer.py
from src.infer.infer import NewsInferencer


class NewsInferencerWrapper:
    """
    Wrapper để tách backend khỏi code ML gốc
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = NewsInferencer()
        return cls._instance

    def infer(self, news_input: dict) -> dict:
        return self.get_instance().infer(news_input)
