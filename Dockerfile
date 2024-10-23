FROM tiagopeixoto/graph-tool
WORKDIR /usr/src/app
RUN pacman -Sy python-pip --noconfirm && pacman -S python-sympy python-shapely --noconfirm
RUN pip install descartes --break-system-packages
