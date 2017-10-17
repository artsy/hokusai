# TODO

## Updates

- deployment subcommand (update / rollback / history / refresh)
- Git tagging
- Configurable tagging scheme?
- Replace hacky kubectl commands with json loaders / formatting options
- Use paging in output formatters where appropriate
- Clean up tagging in git repo / pip beta releases

## Documentation

- Artsy's config and on CI integration (example)
- Deployment / Tagging schema explanation / diagram
- WORKFLOW: commit -> build -> unit tests -> merge ->  integration tests -> push -> deploy -> acceptance tests -> promote

## Tests

- refactor long methods
- cli
- libs
- services (fixtures)
- Docker / Docker-Compose integrations
- Integrations against kubernetes context
- CI (Circle?) Build matrix against Docker / Docker-Compose / Kubernetes versions
- linting & Pep8 check

## Rollout

- Prepare v1 release
- Engineering demo
- Write blog post (with Ashkan)
