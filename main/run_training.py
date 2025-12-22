import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from src.main.run_preprocessing import run_preprocessing
from src.train.train import train
from src.train.evaluate import evaluate

print("ĐANG TIỀN XỬ LÝ DỮ LIỆU")
run_preprocessing(os.path.join(root_dir,"dataset/data_raw/vietnamese_news_dataset.csv"))
print("ĐÃ TIỀN XỬ LÝ DỮ LIỆU")

print("\nĐANG HUẤN LUYỆN")
train(os.path.join(root_dir,"dataset/data_processed"))
print("ĐÃ HUẤN LUYỆN")

print("\nĐANG ĐÁNH GIÁ")
evaluate(os.path.join(root_dir,"dataset/data_processed"))
print("ĐÃ ĐÁNH GIÁ")