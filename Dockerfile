FROM tiagopeixoto/graph-tool
# set work directory
WORKDIR /usr/src/app

# Needed for pycurl
COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pacman -Sy python-pip --noconfirm\
    && pacman -S python-sympy python-shapely --noconfirm

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
