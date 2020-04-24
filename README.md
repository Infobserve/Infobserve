# Infobserve

## Overview

**Infobserve** is an information scanner that ingests, analyzes and classifies data created from various sources that have a potential to leak sensitive information for an organization or individual. It inspired by various OSINT tools and although it can (eventually) be used as a full blown credential scraper, we strongly believe in the motto ***"This technology could fall into the right hands!" So Fork us!***

## Documentation

> Haha! Good one Jim!

But seriously, it's coming at *some* point!

## Requirements

The project started as a practice to build something beautiful with python. Despite the bad reputation the language sometimes gets, we aim to have as few external dependencies as possible. That being said, below you can find the *optional* and **required** ones we just couldn't do without:

* Database
  * Postgres **required**
* Api Keys
  * Github oauth token *optional* (required for enabling the Github source)

## Hacking

* make sure you have [poetry installed](https://python-poetry.org/docs/)
* clone & cd into the repo
* `poetry install `
* `poetry shell`
* You are ready to hack it!

### Docker-compose

You can use the command below to run your code changes instantly:

* `docker-compose build && docker-compose up`

## Data sources

### Gists

### Pastebin

### Gitlab

For the gitlab source to work, a gitlab personal access token is required with at least the `read_user` and `read_repository` scopes enabled.
