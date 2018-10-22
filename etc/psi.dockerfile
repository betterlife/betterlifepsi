FROM python:3.6
WORKDIR /opt/psi
ENV DATABASE_URL=postgres://localhost:5432/psi
ENV SECRET_KEY=secret
ENV SECURITY_PASSWORD_SALT=salt
COPY requirements.txt requirements.txt
COPY etc/requirements etc/requirements
RUN pip install -r requirements.txt
COPY etc/bashrc /root/.bashrc
COPY . .
