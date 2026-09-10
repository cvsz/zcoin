.PHONY: install run test lint compose-check prod-build deploy verify release-check

install:
	python -m pip install -r requirements.txt

run:
	uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

test:
	PYTHONPATH=. pytest -q

lint:
	python -m compileall -q app tests

compose-check:
	docker compose config >/dev/null
	docker compose -f docker-compose.prod.yml config >/dev/null

prod-build:
	docker compose -f docker-compose.prod.yml build

deploy:
	./deploy/deploy.sh

verify:
	./deploy/verify.sh

release-check: lint test
	@echo "zCoin release checks passed"
