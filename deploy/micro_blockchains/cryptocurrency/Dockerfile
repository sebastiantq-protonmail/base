FROM python:3.9-slim
WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install gcc cmake ninja-build git openssl libssl-dev -y \
    && apt-get clean

# Clone and build liboqs
RUN git clone --depth=1 https://github.com/open-quantum-safe/liboqs \
    && cd liboqs \
    && cmake -S . -B build -DBUILD_SHARED_LIBS=ON \
    && cmake --build build --parallel \
    && cmake --build build --target install

# Clone and build liboqs-python
RUN git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python \
    && cd liboqs-python \
    && pip install .

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

# Install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app/