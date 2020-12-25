<div style="text-align: center">
    <h1>What Should We Play?</h1>
    <p>A <a href="https://dev.to/devteam/announcing-the-digitalocean-app-platform-hackathon-on-dev-2i1k">DigitalOcean App Platform Hackathon</a> project</p>
</div>

While we've been social distancing, on lockdown, or apart from friends during COVID-19, online games have been an awesome way to keep in touch and still feel connected. With so many games online and all kinds of threads full of games to explore, it can be hard to keep track of them all! I built What Should We Play to serve as an index for games which anyone in the community can quickly add new entries to, and a tool that'll randomly pick games out of the index based on your party size!

This project was created for the [DigitalOcean App Platform Hackathon](https://dev.to/devteam/announcing-the-digitalocean-app-platform-hackathon-on-dev-2i1k) and serves as the site's backend. Other repositories are available for the site's [front-end](https://github.com/mm/wswp-frontend) and [admin panel](https://github.com/mm/wswp-admin) built to quickly approve and add in community submissions to the index. All three have been deployed to App Platform together and you can access the site at [whatshouldweplay.xyz](https://whatshouldweplay.xyz), but read on to learn more about the stack and building it yourself!

## Overall Project Stack

- **Backend**: Python (Flask for defining API routes, SQLAlchemy as an ORM), PostgreSQL
- **Frontend**: React, Chakra UI for building the user interface

Private "admin" endpoints used to power the admin panel are authenticated through [Auth0](https://auth0.com/). Besides the private endpoints requiring JWT auth, all of the API endpoints are public to consume the index in whatever way you like!

## Getting started

- If you aren't using Docker, you'll need a PostgreSQL instance to connect to somewhere on your computer.

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

5. Good to go! Feel free to go ahead and get the [frontend](https://github.com/mm/wswp-frontend) set up using the instructions there, or test out the API!

### With Docker

