# What Should We Play?

[![Deploy to DO](https://mp-assets1.sfo2.digitaloceanspaces.com/deploy-to-do/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/mm/wswp/tree/main)

While we've been social distancing, on lockdown, or apart from friends during COVID-19, online games have been an awesome way to keep in touch and still feel connected. With so many games online and all kinds of threads full of games to explore, it can be hard to keep track of them all! I built What Should We Play to serve as an index for games which anyone in the community can quickly add new entries to, and a tool that'll randomly pick games out of the index based on your party size!

This project was created for the [DigitalOcean App Platform Hackathon](https://dev.to/devteam/announcing-the-digitalocean-app-platform-hackathon-on-dev-2i1k) and serves as the site's backend. Other repositories are available for the site's [front-end](https://github.com/mm/wswp-frontend) and [admin panel](https://github.com/mm/wswp-admin) built to quickly approve and add in community submissions to the index. All three have been deployed to App Platform together and you can access the site at [whatshouldweplay.xyz](https://whatshouldweplay.xyz), but read on to learn more about the stack and building it yourself!

## Overall Project Stack

- **Backend**: Python (Flask for defining the API, SQLAlchemy as an ORM), PostgreSQL
- **Frontend**: React, Chakra UI for building the user interface

Private "admin" endpoints used to power the admin panel are authenticated through [Auth0](https://auth0.com/). Besides the private endpoints requiring JWT auth, all of the API endpoints are public to consume the index in whatever way you like!

## Getting started

If you aren't using Docker, you'll need a PostgreSQL instance to connect to somewhere on your computer. 

If you'd like to test drive the admin functionality (where you can approve/deny submissions), sign up for [Auth0](https://auth0.com) and keep track of your Auth0 domain. Create an API and single-page application and make note of the API audience and client ID as these will end up being used for environment variables. To disable private endpoints, just pass `ADMIN_OFF=1` as an env variable. The application doesn't require them.

### With Docker

1. Clone this repository: `git clone https://github.com/mm/wswp.git`
2. If you're using Auth0, create a `.env` file in the project root dir with:

    ```
    AUTH0_DOMAIN=your-domain.auth0.com
    AUTH0_API_AUDIENCE=your-api-audience-at-auth0
    ```

3. Build and bring the Docker containers online: `docker-compose up`
4. In a separate terminal, run the database migration scripts and seed the database (only needs to be done once):

    ```console
    docker-compose run api flask db upgrade
    docker-compose run api flask admin seed-db
    ```

5. That's all there is to it! Feel free to head over to the [frontend](https://github.com/mm/wswp-frontend) repo and follow the instructions there to get that set up, or test out the API! The base URL for all requests will be `localhost:8000/v1` unless you've set something up otherwise.

### Without Docker

1. Clone this repository: `git clone https://github.com/mm/wswp.git`

2. Install all dependencies with Pipenv: `cd wswp && pipenv install`

3. Edit the `.env.example` file and populate these environment variables:

    * `FLASK_ENV` can be development while developing
    * `DATABASE_URL`: The connection string to access your PostgreSQL instance. See docs at [SQLAlchemy](https://docs.sqlalchemy.org/en/13/core/engines.html#postgresql) for how to format it.
    * `ADMIN_OFF`: Set this to `1` if you want to disable the admin endpoints (you don't need them to test out the main website/API)
    * `AUTH0_DOMAIN`: If you want to test out the auth flows, sign up for an Auth0 account (it's free!) and input your Auth0 domain here.
    * `AUTH0_API_AUDIENCE`: Create an API in Auth0. Whatever you use as the audience there should be put here.

4. Spawn a shell session with Pipenv and run the database migration scripts to set up your database, then start the dev server locally:

    ```console
    pipenv shell
    flask db upgrade
    flask admin seed-db
    flask run
    ```

5. Good to go! Feel free to go ahead and get the [frontend](https://github.com/mm/wswp-frontend) set up using the instructions there, or test out the API! The base URL for all requests will be `localhost:5000/v1` unless you've set something up otherwise.

## Using the API

The backend exposes a couple public API endpoints (subject to rate limiting), that anyone can use in their applications. All timestamps are returned in UTC and responses are all in JSON. Errors are also returned with a JSON payload describing what happened.

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

