import joblib
import pandas as pd
import xgboost as xgb
from pydantic import BaseModel
from sklearn.preprocessing import MinMaxScaler

from application.dependencies.config import get_config
from utils.form import as_form


@as_form
class HeartFeatures(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    # chol: float
    # fbs: float
    restecg: float
    thalch: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float


config = get_config()

# model_file = config.models_dir / "best_xgb_model.json"
# bst = xgb.Booster(model_file=model_file)

model_file = config.models_dir / "best_model_xgboost.json"
xgb_model = xgb.XGBClassifier()
xgb_model.load_model(model_file)

scalers_file = config.models_dir / "scalers.pkl"
min_max_scalers: dict[str, MinMaxScaler] = joblib.load(scalers_file)


def _scale_features(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    scaled_columns = ["oldpeak", "thalch", "trestbps", "age"]
    for col in scaled_columns:
        result[col] = min_max_scalers[col].transform(result[[col]])
    return result


def predict(features: HeartFeatures) -> float:
    df = pd.DataFrame.from_dict(dict(features), orient="index").transpose()
    scaled = _scale_features(df)
    # dmat = xgb.DMatrix(df)
    return xgb_model.predict(scaled).item()
    # return bst.predict(dmat).item()
