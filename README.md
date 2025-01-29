# Architecture Patterns with Python Exercises
This repository contains all the exercises in [Architecture Patterns with Python](https://www.cosmicpython.com/)
book. Each chapter has its own branch for pursual.

---

## Table of Contents

- **[Chapter 1: Domain Modeling](https://www.cosmicpython.com/book/chapter_01_domain_model.html)**
  - Status: *DONE*
  - Git tag: [ch01](https://github.com/jamescarr/cosmicpython/tree/ch01)

- **[Chapter 2: Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)**
  - Status: *DONE*
  - Git tag: [ch02](https://github.com/jamescarr/cosmicpython/tree/ch02)

- **[Chapter 4: Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer.html)**
  - Status: *DONE*
  - Git tag: [ch04](https://github.com/jamescarr/cosmicpython/tree/ch04)

- **[Chapter 5: Service Layer](https://www.cosmicpython.com/book/chapter_05__high_gear_low_gear.html)**
  - Status: *DONE*
  - Git tag: [ch05](https://github.com/jamescarr/cosmicpython/tree/ch05)

- **[Chapter 6: Unit of Work Pattern](https://www.cosmicpython.com/book/chapter_06_uow.html)**
  - Status: *DONE*
  - Git tag: [ch06](https://github.com/jamescarr/cosmicpython/tree/ch06)

- **[Chapter 7: Aggregates and Consistency Boundaries](https://www.cosmicpython.com/book/chapter_07_aggregate.html)**
  - Status: *DONE*
  - Git tag: [ch07](https://github.com/jamescarr/cosmicpython/tree/ch07)

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
