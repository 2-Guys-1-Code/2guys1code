ARG APP_NAME=poker
ARG APP_PATH=/opt/$APP_NAME
ARG PYTHON_VERSION=3.10.4
ARG POETRY_VERSION=1.2.2


#pipx install poetry==1.2.0
#https://python-poetry.org/docs/#ci-recommendations

#
# Stage: base
#
FROM python:$PYTHON_VERSION as base
ARG APP_NAME
ARG APP_PATH
ARG POETRY_VERSION

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1
ENV \
    POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
# Install Poetry - respects  $POETRY_HOME, what about  $POETRY_VERSION 
run curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR $APP_PATH
COPY ./poetry.lock ./pyproject.toml ./
COPY ./src/ ./src/


#
# Stage: development
#
FROM base as development
ARG APP_NAME
ARG APP_PATH

# Install project in editable mode and with development dependencies
WORKDIR $APP_PATH
COPY ./tests/ ./tests/
COPY ./pytest.ini ./pytest.ini
RUN poetry install



ENTRYPOINT ["poetry", "run"]
CMD ["pokerapi"]


#
# Stage: build
#
FROM base as build
ARG APP_PATH

WORKDIR $APP_PATH
#RUN poetry build --format wheel
RUN poetry build
RUN poetry export --format requirements.txt --output constraints.txt --without-hashes


#
# Stage: production
#
FROM python:$PYTHON_VERSION as production
ARG APP_NAME
ARG APP_PATH

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Get build artifact wheel and install it respecting dependency versions
WORKDIR $APP_PATH
COPY --from=build $APP_PATH/dist/*.whl ./
COPY --from=build $APP_PATH/constraints.txt ./
RUN pip install ./$APP_NAME*.whl --constraint constraints.txt
ENTRYPOINT ["pokerapi"]