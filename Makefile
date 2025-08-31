build-auth:
	sudo docker build ./auth_service \
		-t auth_service
.PHONY: build-auth

run-auth:
	sudo docker run -p 5000:5000 \
		-e MYSQL_ROOT_PASSWORD=password \
	  	-e MYSQL_HOST=localhost \
	  	-e MYSQL_USER=piush \
	  	-e MYSQL_PASSWORD=password \
	  	-e MYSQL_DB=auth_db \
	  	-e SECRET_KEY=something \
	  	auth_service:latest
