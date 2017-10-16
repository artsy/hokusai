# TODO

## Updates

Merge commands:

local:
	build
	dev
	test

remote:
	stack
	env
	deployment
	promote
	run

- Rollback command
	- deployment update
	- deployment rollback
	- deployment history
	- deployment refresh


- Git tagging
- Replace hacky kubectl commands with json loaders / formatting options
- Use paging in output formatters where appropriate
- Configurable tagging scheme

- Projects to use CircleCI 2.0
- Clean up tagging in repo / old beta releases

## Documentation

- Configuration
- Changelog
- Artsy's config and on CI integration (example)
- Deployment / Tagging schema explanation / diagram
- docstrings?
- WORKFLOW: commit -> build -> unit tests -> merge ->  integration tests -> push -> deploy -> acceptance tests -> promote

## Tests

- refactor error handling
- refactor long methods / closures
- cli
- libs
- services (fixtures)
- Docker / Docker-Compose integrations
- integrations against kubernetes context
- CI (Circle?) Build matrix against Docker / Docker-Compose / Kubernetes versions
- linting & Pep8 check

## Rollout

- Prepare v1 release
- Lunch & learn / engineering demo
- Write blog post (with Ashkan)
