build:
	docker build -t ikamet-results .

run:
	docker run ikamet-results

env: 
	export $(cat env.list | xargs)
