import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from main.run_preprocessing import run_preprocessing
from src.train.train import train
from src.train.evaluate import evaluate

print("ĐANG TIỀN XỬ LÝ DỮ LIỆU")
run_preprocessing("data/vietnamese_news_dataset.csv")
print("ĐÃ TIỀN XỬ LÝ DỮ LIỆU")

print("\nĐANG HUẤN LUYỆN")
train()
print("ĐÃ HUẤN LUYỆN")

print("\nĐANG ĐÁNH GIÁ")
evaluate()
print("ĐÃ ĐÁNH GIÁ")