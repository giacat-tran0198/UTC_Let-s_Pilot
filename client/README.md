# TX_CHAT - Client

## Lancer le projet

Avant toute chose, il faut s'assurer d'avoir installer node.js et npm : [Lien pour télécharger node.js et npm](https://nodejs.org/fr/download/)

Pour lancer le projet il suffit d'installer yarn avec npm : ``npm install yarn -g``.

Ensuite il faut **se déplacer dans le dossier client** du projet et lancer la commande : ``yarn`` pour installer les dépendances.

Une fois cela effectué, il suffit de lancer la commande : ``yarn start``.

## Lancer le projet en HTTPS

Pour lancer le projet en https, il suffit de lancer la commande ``yarn run start_https`` dans le dossier client.

## Build le projet

Pour obtenir une version de production, lancer la commande ``yarn run build``. Une fois la version de production construite, installer ``serve`` avec la commande ``npm install -g serve`` et lancer la commande ``serve -s build`` dans le dossier client pour servir le contenu nouvellement créé par le biais d'un serveur static.

## Lancer un conteneur docker

Pour déployer l'application sous forme de conteneur docker, un ``Dockerfile`` a été créé afin de créer une image docker.

Pour cela, s'assurer d'avoir [installé docker](https://docs.docker.com/get-docker/).

Lancer la commande : ``docker build -t tx_chat:client ./`` dans le dossier client. Cette commande permet de créer une image Docker.

Pour lancer le conteneur il suffit de lancer la commande : ``docker run -d -p 80:80 -p 443:443 tx_chat:client``

## Crédits

Icône conçue par [Freepik](https://www.freepik.com) from [www.flaticon.com](https://www.flaticon.com/fr/)

Images conçues par pch.vector sur [Freepik](https://www.freepik.com)

Icon file download : [Crédits](https://icon-library.com/icon/icon-file-downloads-11.html)
