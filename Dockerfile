# 使用官方 Python 基礎映像
FROM python:3.9-slim

# 安裝必需的系統依賴項
RUN apt-get update && \
    apt-get install -y \
    fonts-noto-cjk \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# 設置工作目錄
WORKDIR /app

# 複製當前目錄的內容到容器的 /app 目錄
COPY . /app

# 複製字體文件到容器的字體目錄
COPY msjh.ttc /usr/share/fonts/truetype/microsoft/

# 更新字體緩存
RUN fc-cache -fv

# 安裝 Python 依賴項
RUN pip install --no-cache-dir -r requirements.txt

# 啟動應用程序
CMD ["python", "app.py"]
