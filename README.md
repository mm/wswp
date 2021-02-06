# What Should We Play?

[![Deploy to DO](https://mp-assets1.sfo2.digitaloceanspaces.com/deploy-to-do/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/mm/wswp/tree/main)

While we've been social distancing, on lockdown, or apart from friends during COVID-19, online games have been an awesome way to keep in touch and still feel connected. With so many games online and all kinds of threads full of games to explore, it can be hard to keep track of them all! I built What Should We Play to serve as an index for games which anyone in the community can quickly add new entries to, and a tool that'll randomly pick games out of the index based on your party size!

![A GIF of the index and pick random game feature](https://media.giphy.com/media/vYLjeALSmxztMwp5Jw/giphy.gif)

This project was created for the [DigitalOcean App Platform Hackathon](https://dev.to/devteam/announcing-the-digitalocean-app-platform-hackathon-on-dev-2i1k) and serves as the site's back-end. Other repositories are available for the site's [front-end](https://github.com/mm/wswp-frontend) and [admin panel](https://github.com/mm/wswp-admin) built to quickly approve and add in community submissions to the index. All three have been deployed to App Platform together and you can access the site at [whatshouldweplay.xyz](https://whatshouldweplay.xyz), but read on to learn more about the stack and building it yourself! You can see my [original hackathon submission post here](https://dev.to/mmascioni/what-should-we-play-a-do-hackathon-submission-36k1).

**Note:** If you're using the Deploy to DigitalOcean button above, please follow the instructions [here](#-deploying-to-digitalocean) to initialize the database and get the front-end and back-end talking to each other.

## Table of Contents

- [Overall Project Stack](#-overall-project-stack)
- [Environment Variables](#-environment-variables)
- [Building the project locally](#-building-the-project-locally)
  - [With Docker](#with-docker)
  - [Without Docker](#without-docker)
- [Running Tests](#-running-tests)
- [Deploying to DigitalOcean](#-deploying-to-digitalocean)
- [Using the API](#-using-the-api)
  - [Game Schema](#game-schema)
  - [GET /pulse](#get-pulse)
  - [GET /games](#get-games)
  - [GET /games/:id](#get-gamesid)
  - [GET /games/random](#get-gamesrandom)
  - [GET /games/search](#get-gamessearch)

## 📚 Overall Project Stack

- **Back-end**: Python (Flask for defining the API, SQLAlchemy as an ORM), PostgreSQL
- **Front-end**: React, Chakra UI for building the user interface

Private "admin" endpoints used to power the admin panel are authenticated through [Auth0](https://auth0.com/). Besides the private endpoints requiring JWT auth, all of the API endpoints are public to consume the index in whatever way you like!

## 🔖  Environment Variables

No matter where you're deploying the project, these environment variables control some of the back-end's behaviour. `.env` files are read in automatically if you're developing locally.

* `FLASK_ENV`: Can be "development" while developing
* `DATABASE_URL`: The connection string to access your PostgreSQL instance. See docs at [SQLAlchemy](https://docs.sqlalchemy.org/en/13/core/engines.html#postgresql) for how to format it. This is already taken care of as `${db.DATABASE_URL}` if you're deploying to DigitalOcean via the button

To add in Sentry logging, add these environment variables:

* `SENTRY_DSN`: The Sentry [data source name](https://docs.sentry.io/product/sentry-basics/dsn-explainer/)
* `SENTRY_ENVIRONMENT`: The Sentry [environment](https://docs.sentry.io/product/sentry-basics/environments/)

If you'd like to test drive the admin functionality (where you can approve/deny submissions), sign up for [Auth0](https://auth0.com) and keep track of your Auth0 domain. Create an API and single-page application and make note of the API audience and client ID as these will end up being used for environment variables:

* `ADMIN_OFF`: Set this to `1` if you want to disable the admin endpoints (you don't need them to test out the main website/API)
* `AUTH0_DOMAIN`: If you want to test out the auth flows, sign up for an Auth0 account (it's free!) and input your Auth0 domain here
* `AUTH0_API_AUDIENCE`: Create an API in Auth0. Whatever you use as the audience there should be put here

## 🔨 Building the project locally

If you aren't using Docker, you'll need a PostgreSQL instance to connect to somewhere on your computer. 

### With Docker

1. Clone this repository: `git clone https://github.com/mm/wswp.git`
2. If you're using Auth0, create a `.env` file in the project root dir with:

    ```
    AUTH0_DOMAIN=your-domain.auth0.com
    AUTH0_API_AUDIENCE=your-api-audience-at-auth0
    ```

3. If you want to set up Sentry logging, populate the `SENTRY_DSN` and `SENTRY_ENVIRONMENT` variables in the same `.env` file with your DSN and environment name.
4. Build and bring the Docker containers online: `docker-compose up`
5. In a separate terminal, run the database migration scripts and seed the database (only needs to be done once):

    ```console
    docker-compose run api flask db upgrade
    docker-compose run api flask admin seed-db
    ```

6. That's all there is to it! Feel free to head over to the [frontend](https://github.com/mm/wswp-frontend) repo and follow the instructions there to get that set up, or test out the API! The base URL for all requests will be `http://localhost:8000/v1` unless you've set something up otherwise.

### Without Docker

1. Clone this repository: `git clone https://github.com/mm/wswp.git`

2. Install all dependencies with Pipenv: `cd wswp && pipenv install`

3. Edit the `.env.example` file and populate the environment variables described in [Environment Variables](#environment-variables). Remove any you won't be using (i.e. if you don't want to set up Sentry logging, you can remove the `SENTRY_` variables). Save this as `.env`.

4. Spawn a shell session with Pipenv and run the database migration scripts to set up your database, then start the dev server locally:

    ```console
    pipenv shell
    flask db upgrade
    flask admin seed-db
    flask run
    ```

5. Good to go! Feel free to go ahead and get the [frontend](https://github.com/mm/wswp-frontend) set up using the instructions there, or test out the API! The base URL for all requests will be `localhost:5000/v1` unless you've set something up otherwise.

## ✅ Running Tests

A dedicated Docker Compose file is available for spinning up a test environment to run tests against API endpoints. Pytest can be run within that to run all tests:

```console
docker-compose -f docker-compose.test.yml run --rm testapi pytest
```

Or running specific test modules:

```console
docker-compose -f docker-compose.test.yml run --rm testapi pytest tests/test_submission.py
```

## 🚀 Deploying to DigitalOcean

Due to a current limitation with the Deploy to DigitalOcean button, using this button will only deploy the back-end (the frontend won't be included). You can leave any environment variables that don't apply to your deployment blank. Once the back-end has finished deploying, go to your app in the App Platform console and click on the "Console" tab. Enter these two commands to get the database initialized and seeded with some games to start out:

```console
flask db upgrade
flask admin seed-db
```

Afterwards, you're ready to go! It's time to deploy the front-end. You can do this one of two ways:

* Using the "Deploy to DigitalOcean" button on the [front-end repository](https://github.com/mm/wswp-frontend). Make sure to set the environment variable `REACT_APP_API_URL` to `https://your-app-slug.ondigitalocean.app/api/v1`. 

* By forking the [front-end repository](https://github.com/mm/wswp-frontend) to your account and adding it as a static site component to your current back-end project (more instructions are in the [front-end repository](https://github.com/mm/wswp-frontend)). In this case, you want to set your `REACT_APP_API_URL` to `${APP_URL}/api/v1`, since it lives in the same project.

## 👾 Using the API

The back-end exposes a couple public REST API endpoints (subject to rate limiting), that anyone can use in their applications. All timestamps are returned in UTC and responses are all in JSON. Errors are also returned with a JSON payload describing what happened.

For the live API, the base URL for requests is `https://api.whatshouldweplay.xyz/v1`. No authentication is required on these public methods.

### Game Schema

Whenever games are returned, they'll follow this schema:

* `id`: The identifier for the game in the database (int)
* `name`: The name of the game (string)
* `created_date`: The date & time the game was added to the database (in UTC) (string)
* `description`: A description of the game (string)
* `min_players`: The minimum number of players for the game (int)
* `max_players`: The maximum number of players for the game (int)
* `paid`: Whether the game costs money to play (boolean)
* `submitted_by`: Who submitted the game (string)
* `url`: The URL you can access the game at. Must include `http://` or `https://` protocol (string)

### GET /pulse

Simple status check to make sure the API is online. Returns a `200` with:

```json
{
  "message": "API is online"
}
```

### GET /games

Returns a list of games currently in the database. Results are paginated (can be controlled by query params) and are sorted by the time they were added in (descending)

* Query Params:
    * `page`: The page of game results to fetch (default `1`)
    * `per_page`: The number of games to return per page (default `20`)
    * `price`: Can be `free` or `paid` to show only free or paid games, respectively

**Example Request**: `GET /games?per_page=10`

```json
{
  "games": [
    {
      "created_date": "2020-12-24T04:44:48.189714",
      "description": "Online unofficial Codenames-based game. Each team works together with their Codemaster to uncover their code words.",
      "id": 13,
      "max_players": null,
      "min_players": 4,
      "name": "Codewords",
      "paid": false,
      "submitted_by": "Matt",
      "url": "https://netgames.io/games/codewords/"
    },
    ...
  ],
  "next_page": 2,
  "page": 1,
  "per_page": 10,
  "total_pages": 2
}
```

### GET /games/:id

Fetches a game by its ID (not exposed on the front-end)

* Path parameters:
    * `id`: The ID of the game (integer)

**Example Request**: `GET /games/6`

```json
{
  "game": {
    "created_date": "2020-12-24T04:44:48.187306",
    "description": "Online multiplayer Catan-style game.",
    "id": 6,
    "max_players": 5,
    "min_players": 3,
    "name": "Colonist.io",
    "paid": false,
    "submitted_by": "Matt",
    "url": "https://colonist.io/"
  }
}
```

### GET /games/random

Randomly returns one game based on how many players will be playing, and whether only free games should be returned.

* Query parameters:
  * `free_only`: Whether to only return free games (default `false`)
  * `players`: The number of players in your party (int)

**Example request:** `GET /games/random?players=2`

```json
{
  "game": {
    "created_date": "2020-12-24T03:32:52.157672",
    "description": "Online escape room puzzles to work through with friends! Offers pay-what-you-want and free puzzles.",
    "id": 10,
    "max_players": null,
    "min_players": 1,
    "name": "Enchambered",
    "paid": false,
    "submitted_by": "Matt",
    "url": "https://www.enchambered.com/puzzles/"
  }
}
```

### GET /games/search

Searches for games. This does a full-text search in the database of the game titles and descriptions. Results are paginated (can be controlled by query params)

* Query Params:
    * `query`: Query to search for games by (string)
    * `page`: The page of results to return (int, default `1`)
    * `per_page`: The number of results per page (int, default `20`)

**Example request:** `GET /games/search?query=deduction`

```json
{
  "games": [
    {
      "created_date": "2020-12-24T04:44:48.184806",
      "description": "Interactive, deduction-style game. You work as either a crewmate or imposter aboard a spaceship. Crewmates win by completing tasks, imposters win by killing crewmates. Free with ads on iOS/Android, paid for PC",
      "id": 1,
      "max_players": 10,
      "min_players": 4,
      "name": "Among Us",
      "paid": false,
      "submitted_by": "Matt",
      "url": "https://innersloth.itch.io/among-us"
    },...
  ],
  "next_page": null,
  "page": 1,
  "total_pages": 1
```

