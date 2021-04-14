FROM mcr.microsoft.com/playwright:focal

# 更新 python
RUN apt-get update && apt-get install -y python3.8 python3-pip && \
update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 && \
update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# 安装 playwright
RUN python3 -m pip install playwright==1.10.0 && \
python3 -m playwright install

# 安装 dnspython ，这个用来查询域名
RUN python3 -m pip install dnspython
