FROM debian:buster-slim
LABEL description="Mild Blue - Transplant Kidney Matching base image with conda. "
LABEL project="mildblue:txmatching"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y \
     # conda dependencies
     wget bzip2 ca-certificates libglib2.0-0 \
     libxext6 libsm6 libxrender1 \
     git mercurial subversion \
     # conda-forge dependencies
     libxi6 libxfixes3 libxcursor1 libxdamage1 libxcomposite1 \
     libxrandr2 libxinerama1 libx11-6 && \
    apt-get clean

# copy local installation of miniconda
COPY Miniconda3-4.8.3-Linux-x86_64.sh miniconda.sh
# install miniconda
RUN mv miniconda.sh ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
    /opt/conda/bin/conda clean -afy
