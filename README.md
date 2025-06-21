# electroni-business
Project made for university course, which includes mocked online shop.

* [Contents of the repository](#contents)
  * [Prestashop directory](#prestashop)
  * [docker-compose.yml](#docker-compose)
  * [configuration of the docker-compose](#configuration-docker-composeyml)
    * [mySQL](#mysql)
    * [phpMyAdmin](#phpmyadmin)
    * [Prestashop](#prestashop-1)
* [System requirements and dependencies](#system-requirements-and-dependencies)
* [Usage](#usage)
  * [docker-compose](#docker-compose)
  * [Docker usage concerning the project](#docker-usage-concerning-the-project)
  * [Dumps/data REQUIRED](#dump)
* [SSL](#ssl)

# Contents

As it stands for now, the project works and is able to be deployed on docker containers using the docker-compose functionality.

### Prestashop

Most of the files in the `Prestashop` directory are contents of the Prestashop docker instalation, they are conected as local files to running docker container files by the volume defined in `docker-compose.yml`, changes in those files will also happen in the container and vice versa. More files are added after running the container for the first time, those contain unpacked Prestashop files and won't be uploaded to Git repository as they are included in `.gitignore` file.

Prestashop image is built using Dockerfile in `Prestashop/.docker/` directory, most of the changes needed in Prestashop container have to be added there, including changes like adding afterinit scripts.

### docker-compose.yml

Config of the docker configuration, contains instruction for Docker to create appropriate containers, for now those are: Prestashop, mySql, phpMyAdmin.

More about its usage leter on.

### configuration (docker-compose.yml)

Current configuration contains creation of three containers:

#### mySql

    mysql:
      build:
        dockerfile: Dockerfile
        context: ./mysql/.
      ports:
        - "3306"
      volumes:
        - db-data:/var/lib/mysql
      environment:
        MYSQL_ROOT_PASSWORD: prestashop
        MYSQL_DATABASE: prestashop
      restart: always

This definition declares creation of a container made from image of mysql 5 (altered in Dockerfile in `./mysql/Dockerfile`) on port 3306 (in docker internal network) with a named volume to keep database files even if the container is removed.

Environment variables are set in `environment:` section with Prestashop database name and password curently provided.

The container also restarts itself the moment it shuts down for any given reason.

#### phpMyAdmin

    phpmyadmin:
        image: phpmyadmin/phpmyadmin
        links: 
            - mysql:mysql
        ports:
            - 1235:80
        depends_on:
            - mysql
        environment:
            - PMA_HOST=mysql
            - PMA_USER=root
            - PMA_PASSWORD=prestashop

This definition declares creation of a container made from image of current version of phpMyAdmin which allows to access the database using the web interface over the exposed port (ports 1235:80 means that the 80 port from the container's localhost network is exposed to the 1235 port of our PC's localhost).

It will help the development process as the database changes are going to be much easier.

Environment variables contain database connection details, depends_on means the container won't start until the mysql container works and links means that the container links to the mysql container.

#### Prestashop

    prestashop-git:
      build:
        dockerfile: .docker/Dockerfile
        context: ./PrestaShop/.
        args:
          - VERSION=${VERSION:-8.1-apache}
          - USER_ID=${USER_ID:-1000}
          - GROUP_ID=${GROUP_ID:-1000}
      environment:
        DISABLE_MAKE: ${DISABLE_MAKE:-0}
        PS_INSTALL_AUTO: ${PS_INSTALL_AUTO:-1}
        DB_PASSWD: ${DB_PASSWD:-prestashop}
        DB_NAME: ${DB_NAME:-prestashop}
        DB_SERVER: ${DB_SERVER:-mysql}
        DB_PREFIX: ${DB_PREFIX:-ps_}
        PS_DOMAIN: ${PS_DOMAIN:-localhost:8001}
        PS_FOLDER_INSTALL: ${PS_FOLDER_INSTALL:-install-dev}
        PS_FOLDER_ADMIN: ${PS_FOLDER_ADMIN:-admin-dev}
        PS_COUNTRY: ${PS_COUNTRY:-pl}
        PS_LANGUAGE: ${PS_LANGUAGE:-pl}
        PS_DEV_MODE: ${PS_DEV_MODE:-1}
        PS_DEMO_MODE: ${PS_DEMO_MODE:-0}
        PS_HANDLE_DYNAMIC_DOMAIN: ${PS_HANDLE_DYNAMIC_DOMAIN:-1}
        PS_INSTALL_DB: ${PS_INSTALL_DB:-1}
        PS_ENABLE_SSL: ${PS_ENABLE_SSL:-1}
        ADMIN_MAIL: ${ADMIN_MAIL:-ksiazker.obslugaklienta@gmail.com}
        ADMIN_PASSWD: ${ADMIN_PASSWD:-ProffesorDziub1ch}
      command: ["/tmp/wait-for-it.sh", "--timeout=60", "--strict", "mysql:3306", "--", "/tmp/docker_run_git.sh"]
      ports:
        - "8001:80"
        - "8002:443"
      volumes:
        - ./PrestaShop/:/var/www/html:delegated

This is the most important definition of the Prestashop project container, it uses an image made from Dockerfile specified in `Prestashop/.docker/Dockerfile`.

Context means that the Dockerfile will work in specified project,
args specify used parrent image of the apache and user used to get rid of permissions problems.

Environment variables specify Prestashop configuration, most of those settings are described in [Prestashop additional repository description](https://github.com/PrestaShop/docker). Those settings can easly be changed as needed, we can add more or get rid of some, as it stands the Prestashop is already installed with values present in the DB dump so most of them isn't taken into account.

The container is exposed to the ports 8001 (http) and 8002 (https) on the PC.

The volume allows for the files in `Prestashop` directory to be connected to container's files, changes in one of them happen in the other. Delegated added to the volume means that not every change made in the container happens instantaneously on the machine to allow some kind of a failsafe if the container crusher becaouse of some change.

# System requirements and dependencies

## Docker with docker-compose

The project was only tested on Linux version, main part should work on Windows as docker is highly compatible with all main platforms but can't guarantee it. 

Instalation and further help is available at [Docker compose documentation site (Linux)](https://docs.docker.com/compose/install/)

or [main Docker documantation site](https://docs.docker.com/desktop/).

I'm using docker engine with docker cli instead of docker desktop.

## The project also uses:

* Prestashop
* phpMyAdmin
* mySQL

# Usage

## docker-compose

Those are the main commands needed to use this project, all of them should be run in the folder the `docker-compose.yml` file is located in and with root privilages, usage of sudo for each command can be avoided by making a Docker user group with root privilages, the proccess is described in [the docker documentation](https://docs.docker.com/engine/install/linux-postinstall/).

* `docker-compose build` - builds the images used by the containers, should be run if any changes where made to Dockerfile located in `Prestashop/.docker/`, build sections of `docker-compose.yml` or if any new container definition was added in `docker-compose.yml`. If there wasn't any images created yet of those containers on local Docker or they were deleted using `docker image rm IMAGE_NAME` then this step can be skipped and `docker-compose up` will run this command itself. This command can be run whenever needed, the containers can be online during the procedure.
* `docker-compose up` - creates networks, containers and volumes (as needed, if the volume exists it won't get overwritten, the same for network and the containers if they are running, if the containers are stopped they could get overwritten if any changes happened to their images), starts the containers and prints current logs of all containers running (can be used with `-d` flag to detach off of the terminal `docker-compose up -d` and not show any logs). It can be used with container name to only run/restart/recreate one container (`docker-compose up CONTAINER_NAME`).
* `docker-compose down` - stops running containers and then removes them, doesn't do anything to the volumes so the mySQL data is still there. It can be run with `-v` flag to also remove the volumes.

## Docker usage concerning the project

* `docker stop CONTAINER_NAME` - switches off the container, useful if the service run in the container needs to update changed files..
* `docker restart CONTAINER_NAME` - switches on the container, useful if the service run in the container needs to update changed files.
* `docker rm CONTAINER_NAME` - removes the container, needs to be stopped first.
* `docker cp CONTAINER_NAME:PATH PATH` - copies the files from the container to the system the docker runs on, arguments can be switched over to copy from the system to the container. CAN BE USED EVEN IF THE CONTAINER IS STOPPED, useful if the container crushed and we don't won't to recreate it from the image.
* `docker exec` - allows to run a command in a container, for exampe `docker exec -u root -it CONTAINER_NAME /bin/bash` gives bash terminal of the specified container as root, `-it` flag means that the command stays on our terminal with an ability to interact with the effects of the used command `/bin/bash`, `-u root` means the command is executed as root.
* `docker logs` - allows to get to the logs of the container, `-f` flag makes the logs follow current log and `-n NUMBER_OF_LINES` flag makes the command show only specified number of logs, can be used like `docker logs -f -n 100 CONTAINER_NAME`

More commands and much more detailed descriptions are available at [Docker CLI documentation](https://docs.docker.com/engine/reference/run/)

## Dump

The MySQL container won't even build without a dump file (backup) of the database present in `./mysql/`. It has to be named `dump.sql`. Docker will automatically import the dump during container initialization.

# SSL

SSL jest tworzony i konfigurowany automatycznie przy pomocy Dockerfile Prestashopam skryptów i plików w folderze `/Prestashop/.docker/` oraz odpowiedniej konfiguracji bazy danych w dumpie.
