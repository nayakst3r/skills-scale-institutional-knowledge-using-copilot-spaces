# The dbt project as a container, run by the orchestrator (Cloud Run job / ECS task).
FROM python:3.11-slim
WORKDIR /app
COPY requirements-stack.txt ./
RUN pip install --no-cache-dir -r requirements-stack.txt
COPY dbt_project.yml profiles.yml .dbtignore ./
COPY macros macros
COPY domains domains
ENTRYPOINT ["dbt"]
