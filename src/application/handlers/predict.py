import logging
from http import HTTPStatus

import cv2
import numpy as np
from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel

from application.dependencies.ai import heart, pneumonia
from application.dependencies.auth import AuthDep
from application.dependencies.config import ConfigDep
from utils.exceptions import statuses_to_responses

router = APIRouter(
    prefix="/predict",
    tags=["Predict"],
    responses=statuses_to_responses(HTTPStatus.UNAUTHORIZED, HTTPStatus.NOT_FOUND),
)
logger = logging.getLogger(__name__)


class Prediction(BaseModel):
    prediction: float


@router.post("/heart", response_model=Prediction)
async def predict_heart(
    auth: AuthDep, features: heart.HeartFeatures = Depends()
) -> Prediction:
    prediction = heart.predict(features)
    prediction = round(prediction, 3)
    return Prediction(prediction=prediction)


@router.post("/pneumonia", response_model=Prediction)
async def predict_pneumonia(
    lung_scan: UploadFile, auth: AuthDep, config: ConfigDep
) -> Prediction:
    buffer = await lung_scan.read()
    arr = np.frombuffer(buffer, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    cv2.imwrite(str(config.log_dir / "upload_color.jpeg"), img)
    prediction = pneumonia.predict(img)
    prediction = round(prediction, 3)
    return Prediction(prediction=prediction)
