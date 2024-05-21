import logging
from pathlib import Path

import cv2
import pydicom as dicom
import pydicom.uid as uid

logger = logging.getLogger(__name__)


def dicom_to_image(dcm_path: Path, image_path: Path) -> tuple[int, int]:
    logger.debug(image_path)
    ds = dicom.dcmread(dcm_path, force=True)
    # ds.file_meta.TransferSyntaxUID = uid.ImplicitVRLittleEndian
    pixels = cv2.flip(ds.pixel_array, 0)
    cv2.imwrite(str(image_path), pixels)
    height, width = ds.pixel_array.shape
    return height, width
