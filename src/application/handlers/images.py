from __future__ import annotations

import io
import logging
import operator
import os
import shutil
import tempfile
import zipfile
from collections.abc import Sequence
from http import HTTPStatus
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from application.dependencies.auth import AuthDep
from application.dependencies.config import ConfigDep
from domain.entities.jwt import AuthRole
from utils import dicom2image
from utils.exceptions import statuses_to_responses

router = APIRouter(
    prefix="/images",
    tags=["Images"],
    responses=statuses_to_responses(HTTPStatus.UNAUTHORIZED, HTTPStatus.NOT_FOUND),
)
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png"]


class Dicom(BaseModel):
    name: str
    path: str
    type: Literal["dicom"]


class Dir(BaseModel):
    type: Literal["dir"]
    name: str
    path: str
    children: Sequence[Node]


Node = Annotated[Dicom | Dir, Field(discriminator="type")]

get_name = operator.attrgetter("name")


def scan_dicoms_dir(root: Path, current_dir: Path, target_ext: str) -> Dir:
    dirs: list[Dir] = []
    dicoms: list[Dicom] = []

    for child in current_dir.iterdir():
        if child.is_dir():
            child_dir = scan_dicoms_dir(root, child, target_ext)
            dirs.append(child_dir)
        elif child.suffix.lower() == ".dcm":
            child_dicom = Dicom(
                type="dicom",
                name=child.name,
                path=str(child.relative_to(root).with_suffix("." + target_ext)),
            )
            dicoms.append(child_dicom)

    return Dir(
        type="dir",
        name="." if current_dir == root else current_dir.name,
        path="." if current_dir == root else str(current_dir.relative_to(root)),
        children=sorted(dirs, key=get_name) + sorted(dicoms, key=get_name),
    )


@router.get("/sources/{dir_path:path}")
async def download_sources(dir_path: str, auth: AuthDep, config: ConfigDep):
    if AuthRole.ADMIN not in auth.roles:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "you are not authorized for this operation"
        )

    target_dir = config.dicom_dir / dir_path
    if not target_dir.exists():
        raise HTTPException(HTTPStatus.NOT_FOUND, "directory not found")

    _, tempfile_path = tempfile.mkstemp(".zip")

    with zipfile.ZipFile(tempfile_path, mode="w") as archive:
        for filepath in target_dir.rglob("*"):
            archive.write(filepath, arcname=filepath.relative_to(target_dir))

    cleanup = BackgroundTask(os.unlink, tempfile_path)

    return FileResponse(
        tempfile_path,
        filename=f"{target_dir.name}.zip",
        background=cleanup,
    )


@router.get("/list{dir_path:path}", response_model=Dir)
async def list_images(
    dir_path: str = "", ext: str = "jpg", *, auth: AuthDep, config: ConfigDep
):
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(HTTPStatus.NOT_FOUND)
    target_dir = config.dicom_dir / dir_path.removeprefix("/")
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(HTTPStatus.NOT_FOUND)
    return scan_dicoms_dir(config.dicom_dir, target_dir, ext)


@router.get("/{image_path:path}", response_class=FileResponse)
async def get_image(image_path: str, auth: AuthDep, config: ConfigDep):
    path_parts = image_path.rsplit(".", 1)
    if len(path_parts) != 2:
        logger.error("bad path")
        raise HTTPException(HTTPStatus.NOT_FOUND)

    filepath, ext = path_parts
    if ext.lower() not in ALLOWED_IMAGE_EXTENSIONS:
        logger.error("bad image extension")
        raise HTTPException(HTTPStatus.NOT_FOUND)

    dcm_path = config.dicom_dir / (filepath + ".dcm")
    if not dcm_path.exists():
        logger.error(f"no such file {dcm_path.resolve()}, ({config.dicom_dir = })")
        raise HTTPException(HTTPStatus.NOT_FOUND)

    output_path = config.images_dir / (filepath + "." + ext)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        height, width = dicom2image.dicom_to_image(dcm_path, output_path)
        logger.info(f"{height = }, {width = }")
    except Exception:
        logger.error("could not convert file to image")
        raise HTTPException(HTTPStatus.NOT_FOUND)

    return FileResponse(output_path)


@router.post("/upload/{dir_path:path}")
async def upload_images(
    file: UploadFile, dir_path: str, auth: AuthDep, config: ConfigDep
):
    if AuthRole.ADMIN not in auth.roles:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "you are not authorized for this operation"
        )

    target_dir = config.dicom_dir / dir_path
    # if target_dir.exists():
    #     raise HTTPException(HTTPStatus.BAD_REQUEST, "directory name taken")

    logger.info(f"{file.filename = }, {file.content_type = }")
    contents = await file.read()
    buffer = io.BytesIO(contents)
    with zipfile.ZipFile(buffer) as archive:
        for f in archive.infolist():
            if not f.filename.lower().endswith(".dcm"):
                raise HTTPException(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    f'bad file "{f.filename}"',
                )
            if (target_dir / f.filename).exists():
                raise HTTPException(
                    HTTPStatus.UNPROCESSABLE_ENTITY,
                    f'filename "{f.filename}" already taken',
                )
        archive.extractall(target_dir)


@router.delete("/{dir_path:path}")
async def delete_images_dir(dir_path: str, auth: AuthDep, config: ConfigDep):
    if AuthRole.ADMIN not in auth.roles:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "you are not authorized for this operation"
        )

    target_dir = config.dicom_dir / dir_path
    if not target_dir.exists() or not target_dir.is_dir():
        raise HTTPException(HTTPStatus.BAD_REQUEST, "no such directory")

    if (
        target_dir.samefile(config.dicom_dir)
        or config.dicom_dir.resolve() not in target_dir.resolve().parents
    ):
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "you are not authorized for this operation"
        )

    shutil.rmtree(target_dir)
