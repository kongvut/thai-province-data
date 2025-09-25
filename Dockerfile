FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ติดตั้ง dependency ที่สคริปต์ต้องใช้
# - 0_validate_data.py ใช้ stdlib
# - 1_export_file_format.py / make.py ต้องมี pandas + openpyxl เพื่อ export .xlsx
RUN pip install --upgrade pip && \
    pip install pandas openpyxl
