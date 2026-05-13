#!/usr/bin/env python3
"""Gera dbt/profiles.yml a partir de DATABASE_URL — usado em CI (GitHub Actions)."""
import os
import urllib.parse

url = os.environ["DATABASE_URL"]
u = urllib.parse.urlparse(url)
dbname = u.path.lstrip("/").split("?")[0]

content = f"""brasilibid:
  target: prod
  outputs:
    prod:
      type: postgres
      host: {u.hostname}
      user: {u.username}
      password: {u.password}
      port: {u.port or 5432}
      dbname: {dbname}
      schema: public
      sslmode: require
      connect_timeout: 30
"""

with open("dbt/profiles.yml", "w") as f:
    f.write(content)

print("✅ dbt/profiles.yml gerado")
