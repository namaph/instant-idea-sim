.PHONY: run
run:
	docker build --pull --rm -f "Dockerfile" -t namaphsim:latest "."
	docker run --rm -it -p 8000:8000 namaphsim bash`


.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' | xargs rm -rf
	@find . -type d -name '*.ropeproject' | xargs rm -rf
	@rm -rf build/
	@rm -rf dist/
	@rm -f src/*.egg*
	@rm -f MANIFEST
	@rm -rf docs/build/
	@rm -f .coverage.*

.PHONY: lint
lint:
	poetry run tox -e lint

.PHONY: test
test:
	poetry run tox -e py39