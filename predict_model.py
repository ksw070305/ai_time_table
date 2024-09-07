# 필요한 라이브러리 불러오기
import pickle
import json
import calendar as cl
import sqlite3
from datetime import datetime, date

def predict(target_grade, model_path):
    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    # 예측할 데이터 준비하기 (예: X_new)
    X_new = [[float(target_grade)]]  # 새로운 데이터

    # 예측 수행하기
    predictions = model.predict(X_new)

    return predictions


def time_blocking(required_time_dic):
    time_block_list = []
    for key,value in required_time_dic.items():
        for i in range(value):
            time_block_list.append(f"{key}:1hour")

    return time_block_list

print(predict(1,"C:/project/ai_time_table/models/english(g-t).pkl"))