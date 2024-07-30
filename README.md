

# RMF2 Web

RMF2 Web is an extension of Open-RMF Web. It is an effort to make the UI components more user friendly and abstract from RMF. Changes are done mainly on the API server, which acts as a bridge between the Healthcare Integrator (HI) mobile app and Chart-RMF. RMF dashboard is still compatible with the updated API server, usually for robot task monitoring. 

> **Note**
> HI package is not part of RMF2 Web

Updated features include:
- Task Packages
- Enhanced Alerts
- Event Driven Task (bed exit & blanket milk run)

Packages
- [Getting started](#getting-started)
- [API server](packages/api-server)
- [API client](packages/api-client)
- [Dashboard](packages/dashboard)
- [Configuration](#configuration)

# Getting started

### Prerequisites

We currently support [Ubuntu 22.04](https://releases.ubuntu.com/jammy/), [ROS 2 Humble](https://docs.ros.org/en/humble/index.html) and CHART-RMF's [AP1](https://github.com/chart-sg/rmf2_ros2/tree/development) branch. Other distributions may work as well, but is not guaranteed.

Install [nodejs](https://nodejs.org/en/download/package-manager/) >= 16,
```bash
sudo apt update && sudo apt install curl
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
nvm install 16
```

Install pnpm and nodejs
```bash
curl -fsSL https://get.pnpm.io/install.sh | bash -
pnpm env use --global 16
```

Install pipenv
```bash
pip3 install pipenv
```

For Debian/Ubuntu systems, you may need to install `python3-venv` first.
```bash
sudo apt install python3-venv
```

### PostgreSQL
The API server makes use of PostgreSQL 'bare metal'. The defaults are for PostgreSQL to be listening on 127.0.0.1:5432.

#### Bare Metal
```
apt install postgresql postgresql-contrib -y
# Set a default password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

sudo systemctl restart postgresql
# interactive prompt
sudo -i -u postgres
```
To manually reset the database:
```
sudo -u postgres bash -c "dropdb postgres; createdb postgres"
```

### Installing Chart-RMF

Refer to the following documentation for building from source. Please refer to 'development' branch

* [rmf](https://github.com/chart-sg/rmf2_main/tree/development)

> **Note**
> AP1 Simulation demo is currently not available in Chart-RMF

### Install dependencies

Run
```bash
pnpm install
```

You may also install dependencies for only a subset of the packages
```bash
pnpm install -w --filter <package>...
```

### Launching
The API server should be started manually to work with RMF-Chart deployment on another terminal instance.

Source Chart-RMF and launch the API server.

> **Note**
> Prior to launching API server, RMF 2.0 sensor manager should be running. 
This is because the API server waits for ROS Action server on launch.
### API server
```bash
# For binary installation
source /opt/ros/humble/setup.bash

# For source build
source /path/to/workspace/install/setup.bash

# start API server in development mode
cd packages/api-server
pnpm start:dev
```

This starts up the API server (by default at port 8000) which sets up endpoints to communicate with an Chart-RMF deployment.

Ensure that the fleet adapters in the Chart-RMF deployment is configured to use the endpoints of the API server, `http://[SERVER_URI]:8000/_internal`. 

Launching pimo fleet adapter for example, the command would be,

```bash
ros2 launch ff_panasonic piimo_robot_adapter.launch.xml server_uri:="http://10.233.29.67:8000/_internal"
```


### RMF dashboard (optional)

Once the dashboard the built is completed, it can be viewed at [SERVER_URI:3000](http://localhost:3000).

```bash
cd packages/dashboard
pnpm run build

# Once completed
npm install -g serve
serve -s build
```

## Postman (optional) 
Instead of using the HI UI, the api requests can be triggered using postman.
Import the following RMF API server collection and environment from the [postman folder](packages/api-server/postman/)

# Configuration

Make changes to [AP1 dev config](packages/api-server/chart_dev_config.py) for items related to 
* robot name / fleet
* switching events on / off
* ip address
* delay timings

# Contribution guide

* For general contribution guidelines, see [CONTRIBUTING](CONTRIBUTING.md).
* Follow [typescript guidelines](https://basarat.gitbook.io/typescript/styleguide).
* When introducing API changes with [`api-server`](packages/api-server),
  * If the new changes are to be used externally (outside of the web packages, with other Open-RMF packages for example), make changes to [`rmf_api_msgs`](https://github.com/open-rmf/rmf_api_msgs), before generating the required models using [this script](packages/api-server/generate-models.sh) with modified commit hashes.
  * Don't forget to update the API client with the newly added changes with [these instructions](packages/api-client/README.md/#generating-rest-api-client).
* Check out the latest API definitions [here](https://open-rmf.github.io/rmf-web/docs/api-server), or visit `/docs` relative to your running server's url, e.g. `http://localhost:8000/docs`.
* Develop the frontend without launching any Open-RMF components using [storybook](packages/dashboard/README.md/#storybook).


