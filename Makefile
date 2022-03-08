.PHONY: run
run:
	docker build --pull --rm -f "Dockerfile" -t namaphsim:latest "."
	docker run --rm -it -p 8000:8000 namaphsim bash`


.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' | xargs rm -rf
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .mypy_cache/
	@rm -rf .pytest_cache/
	@rm -rf .tox/
	@rm -f .coverage.*

.PHONY: lint
lint:
	poetry run tox -e lint

.PHONY: test
test:
	poetry run tox -e py39

.PHONY: start
start:
	poetry run uvicorn --host 0.0.0.0 --port 8000 instant_sim.main:app