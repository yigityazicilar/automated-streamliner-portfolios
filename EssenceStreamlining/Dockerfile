FROM conjurecp/conjure-runtime

RUN apt-get update && apt-get install -y git curl wget build-essential libreadline-gplv2-dev libncursesw5-dev \
     libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev libnuma-dev cmake lbzip2 jq

# Download and install stack for Haskell build
RUN curl -sSL https://get.haskellstack.org/ | sh
#
## Install conjure streamlining variant
RUN cd /opt && git clone https://github.com/conjure-cp/conjure.git && cd conjure && git checkout streamlining && make
#
## Install python
RUN wget https://www.python.org/ftp/python/3.9.4/Python-3.9.4.tgz && tar xzf Python-3.9.4.tgz && cd Python-3.9.4 && ./configure --enable-optimizations \
	&& make install
#
## Install runsolver
RUN cd /opt && wget https://www.cril.univ-artois.fr/~roussel/runsolver/runsolver-3.4.0.tar.bz2 && tar xvf runsolver-3.4.0.tar.bz2 \
	&& cd runsolver/src && make install
#
## Install fzn-chuffed solver
RUN cd /opt && git clone https://github.com/chuffed/chuffed.git && cd chuffed && mkdir build && cd build && cmake .. && cmake --build . --target install

# Copy in Code
COPY ./code /code
# Copy in Examples 
COPY ./examples /examples

## Install necessary dependencies
RUN cd /code && pip3.9 install pipenv && pipenv install
# Set path correctly so we get streamlining variants of executables
ENV PATH /root/.local/bin:$PATH

WORKDIR /code
CMD ["/examples/VesselLoading/", "/examples/VesselLoading/params"]
ENTRYPOINT ["pipenv", "run", "python", "./src/Main.py"]
