help: ## Show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

build-docker-generate: ## Build py-openapi-generator-cli docker images used for code generation
	docker build . -f build/Dockerfile.openapi_generator --tag py-openapi-generator-cli

generate: ## Run openapi-generator to generate controllers and models
	docker run --rm -v "${PWD}:/local" \
		py-openapi-generator-cli generate \
								 --enable-post-process-file \
								 -i /local/pg_backup_api/pg_backup_api/spec/pg_backup_api.yaml \
								 -o /local/pg_backup_api/pg_backup_api \
								 -t /local/generator_templates \
								 -g python-flask \
								 --global-property debugModels=true

test:
	pytest


