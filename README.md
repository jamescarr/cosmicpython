# Architecture Patterns with Python Exercises
This repository contains all the exercises in [Architecture Patterns with Python](https://www.cosmicpython.com/)
book. Each chapter has its own branch for pursual.

---

## Table of Contents

- **[Chapter 1: Domain Modeling](https://www.cosmicpython.com/book/chapter_01_domain_model.html)**
  - Status: *DONE*
  - Git tag: [ch01](https://github.com/jamescarr/cosmicpython/tree/ch01)

- **[Chapter 2: Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
  - Status: *DONE*
  - Git tag: [ch02](https://github.com/jamescarr/cosmicpython/tree/ch02)

- **[Chapter 4: Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
  - Status: *IN PROGRESS*
  - Git tag: [ch04](https://github.com/jamescarr/cosmicpython/tree/ch04)


## Development
There is a `Makefile` included with the targets listed when running the default
help target.

```
help                  Show this help message
test                  Run the tests using Poetry and pytest
watch-tests           Run tests continuously using pytest-watch
black                 Run black on the project
api-dev               Runs the API Server
```

## API Server
The API server can be run standalone via `make api-dev` and contains a SwaggerUI
endpoint at `/docs`.
