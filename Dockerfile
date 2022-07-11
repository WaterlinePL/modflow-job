FROM mjstealey/docker-modflow:latest
RUN apt update
RUN apt install -y curl
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y --force-yes nodejs

ARG hf_job_executor_version
ENV HYPERFLOW_JOB_EXECUTOR_VERSION=$hf_job_executor_version

RUN npm install -g @hyperflow/job-executor@${HYPERFLOW_JOB_EXECUTOR_VERSION}
WORKDIR /
RUN apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev wget -y

COPY compile_and_install_openssl.sh compile_and_install_openssl.sh
RUN bash compile_and_install_openssl.sh

COPY compile_and_install_python310.sh compile_and_install_python310.sh
RUN bash compile_and_install_python310.sh

COPY requirements.txt requirements.txt
RUN python3.10 -m pip install -r /requirements.txt

COPY src/ /datapassing/
COPY launch_modflow.sh launch_modflow.sh