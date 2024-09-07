import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

def make_model(fp):
# CSV 파일 경로
    file_path = fp

# CSV 파일 읽기
    data = pd.read_csv(file_path, header=None)

# X와 y 데이터 추출
    X = data.iloc[:, 0].values.reshape(-1, 1)  # 첫 번째 열을 X로 사용, 2차원 배열로 변환
    y = data.iloc[:, 1].values

    # 모델 생성 및 학습
    model = LinearRegression()
    model.fit(X, y)

    u = file_path.split('/')

    # 학습된 모델을 파일로 저장 (pickle)
    model_file = f'{u[-1]}.pkl'
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
