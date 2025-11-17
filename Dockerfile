# Use official Python 3.10 slim image
FROM python:3.10.15-slim

# Set working directory
WORKDIR /api

# Install required system dependencies
# - default-libmysqlclient-dev (needed for MySQL client)
# - build-essential (for compiling deps)
# - libgl1, libglib2.0-0 (needed for OpenCV / image libraries)
# - freetds-dev, freetds-bin (core FreeTDS)
# - unixodbc, unixodbc-dev (ODBC driver manager)
# - tdsodbc (provides libtdsodbc.so for pyodbc)
RUN apt-get update && \
    apt-get install -y \
        default-libmysqlclient-dev \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        freetds-dev \
        freetds-bin \
        unixodbc \
        unixodbc-dev \
        tdsodbc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure FreeTDS ODBC driver
# Detect architecture and configure FreeTDS ODBC driver accordingly
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "arm64" ]; then \
        DRIVER="/usr/lib/aarch64-linux-gnu/odbc/libtdsodbc.so"; \
    else \
        DRIVER="/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so"; \
    fi && \
    echo "[FreeTDS]\n\
Description=FreeTDS Driver\n\
Driver=$DRIVER\n\
Setup=$DRIVER\n\
UsageCount=1\n" > /etc/odbcinst.ini

# Configure DSN for SQL Server 2005
RUN echo "[sql2005]\n\
Driver=FreeTDS\n\
Server=192.168.0.9\n\
Port=1433\n\
Database=exodusdata\n\
TDS_Version=7.0\n" > /etc/odbc.ini

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .
