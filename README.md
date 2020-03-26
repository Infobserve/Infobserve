# Infobserve

## Overview

**Infobserve** is an information scanner that ingests,analyzes and classifies data created from various sources that have a potential to leak sensitive information for an organization or individual. To achieve this it is inspired by various OSINT tools and although it can be used as a full blown credential scraper we strongly believe in the motto ***"This technology could fall into the right hands!" So Fork us!***

## Documentation

> Haha! Good one Jim!

## Requirements

The project started as a practice to build something beautiful with python although the bad reputation the lang sometimes gets we aim to have as few external dependencies requirements as possible but below you can find check for *optional* or **required** tags.

* Database
  * Postgres **required**
* Api Keys
  * Github oauth token *optional*

## Hacking

* clone the repo
* `pip install poetry`
* cd into the repo
* `poetry install --dev`
* Create a dev environment configuration (docker-compose in the oven)
* `poetry shell`
* You are ready to hack it!

### Docker-compose

You can use the command below to run your code changes instantly:
* `docker-compose build && docker-compose up`