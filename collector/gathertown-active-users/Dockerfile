FROM selenium/standalone-chrome
USER root
RUN sudo apt-get update && sudo apt-get install -y python3-distutils
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY *.py /
CMD ["python3", "/main.py"]
