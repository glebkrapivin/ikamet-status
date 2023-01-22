build:
	docker build -t ikamet-results .

run:
	docker run --env-file env.list ikamet-results
