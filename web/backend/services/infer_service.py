from typing import Dict
from web.backend.models.news_inferencer import NewsInferencerWrapper


class InferService:
    """
    Service layer chịu trách nhiệm gọi mô hình AI
    """

    def __init__(self):
        self.inferencer = NewsInferencerWrapper()

    def run_infer(self, news_input: Dict) -> Dict:
        """
        Gọi mô hình và trả về raw model output
        """

        if not isinstance(news_input, dict):
            raise ValueError("news_input must be a dictionary")

        print("news_input:\n",news_input)

        result = self.inferencer.infer(news_input)

        # Validate tối thiểu output model
        if not isinstance(result, dict):
            raise RuntimeError("Model output is not a dictionary")

        if "prediction" not in result:
            raise RuntimeError("Model output missing 'prediction' field")

        print(result)

        return result
