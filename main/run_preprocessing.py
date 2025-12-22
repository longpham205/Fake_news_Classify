#run_preprocessing
import os
import sys
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
import pandas as pd
from preprocessing.preprocess.pipeline import preprocess_dataframe
from preprocessing.preprocess.config import TRAIN_MODE


def run_preprocessing(INPUT_CSV_PATH):
    #==================================
    #Preprocessing
    #==================================

    # ====== 1. ĐƯỜNG DẪN CSV GỐC ======
    print("Đã lấy dữ liệu:",INPUT_CSV_PATH)
    OUTPUT_CSV_PATH = os.path.join(os.path.abspath(os.path.join(os.path.dirname(INPUT_CSV_PATH),"..")),"data_processed/train_processed.csv")

    # ====== 2. LOAD CSV ======
    df = pd.read_csv(INPUT_CSV_PATH)

    # ====== 3. PREPROCESS ======
    processed_df = preprocess_dataframe(df, mode=TRAIN_MODE)

    # ====== 4. SAVE KẾT QUẢ ======
    processed_df.to_csv(OUTPUT_CSV_PATH, index=False)

    print(f"Saved processed data to {OUTPUT_CSV_PATH}")

    #==================================
    #EDA
    #==================================
    from preprocessing.eda.run_eda import run_eda
    print("\nĐang phân tích dữ liệu:")
    run_eda(OUTPUT_CSV_PATH)

    #==================================
    #Split data
    #==================================
    from preprocessing.preprocess.split_data import split
    print("\nĐang chia dữ liệu:")
    split(OUTPUT_CSV_PATH)

if __name__ == "__main__":
    run_preprocessing(os.path.join(root_dir,"dataset/data_raw/vietnamese_news_dataset.csv"))
