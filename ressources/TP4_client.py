"""\
GLO-2000 Travail pratique 4 - Client
Noms et numéros étudiants:
-Jérémy Doiron
-
-
"""

import argparse
import getpass
import json
import socket
import sys

import glosocket
import gloutils


class Client:
    """Client pour le serveur mail @glo2000.ca."""

    def __init__(self, destination: str) -> None:
        """
        Prépare et connecte le socket du client `_socket`.

        Prépare un attribut `_username` pour stocker le nom d'utilisateur
        courant. Laissé vide quand l'utilisateur n'est pas connecté.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((destination, gloutils.APP_PORT))
        except (TimeoutError, InterruptedError):
            sys.exit("Connexion au serveur impossible.")
        self._username = ""

    def _register(self) -> None:
        """
        Demande un nom d'utilisateur et un mot de passe et les transmet au
        serveur avec l'entête `AUTH_REGISTER`.

        Si la création du compte s'est effectuée avec succès, l'attribut
        `_username` est mis à jour, sinon l'erreur est affichée.
        """
        self._username = input("Entrez votre nom d'utilisateur: ")
        password = getpass.getpass("Entrez votre mot de passe: ")
        if self._username and password:
            register = json.dumps(gloutils.GloMessage(
                header=gloutils.Headers.AUTH_REGISTER,
                payload=gloutils.AuthPayload(
                    username=self._username
                    password = password
            )))
        else:
            print("Erreur de registre ")


    def _login(self) -> None:
        """
        Demande un nom d'utilisateur et un mot de passe et les transmet au
        serveur avec l'entête `AUTH_LOGIN`.

        Si la connexion est effectuée avec succès, l'attribut `_username`
        est mis à jour, sinon l'erreur est affichée.
        """

        self._username=input("Entrez votre nom d'utilisateur: ")
        password = getpass.getpass("Entrez votre mot de passe: ")

        if(self._username and password):
            login = json.dumps(gloutils.GloMessage(
                header=gloutils.Headers.AUTH_LOGIN,
                payload=gloutils.AuthPayload(
                    username=self._username
                    password=password
                )))
        else:
            print("Erreur de connexion")

    def _quit(self) -> None:
        """
        Préviens le serveur de la déconnexion avec l'entête `BYE` et ferme le
        socket du client.
        """

    def _read_email(self) -> None:
        """
        Demande au serveur la liste de ses courriels avec l'entête
        `INBOX_READING_REQUEST`.

        Affiche la liste des courriels puis transmet le choix de l'utilisateur
        avec l'entête `INBOX_READING_CHOICE`.

        Affiche le courriel à l'aide du gabarit `EMAIL_DISPLAY`.

        S'il n'y a pas de courriel à lire, l'utilisateur est averti avant de
        retourner au menu principal.
        """

    def _send_email(self) -> None:
        """
        Demande à l'utilisateur respectivement:
        - l'adresse email du destinataire,
        - le sujet du message,
        - le corps du message.

        La saisie du corps se termine par un point seul sur une ligne.

        Transmet ces informations avec l'entête `EMAIL_SENDING`.
        """
        # Récupération des données pour les champs du courriel

        destination:str=input("Entrez l'adresse du destinataire: ")
        subject:str=input("Entrez le sujet: ")

        # La saisie du corps se termine par un point seul sur une ligne.
        print("Body: (enter '.' on a single line to finish typing)")
        body = ""
        buffer = ""
        while (buffer != ".\n"):
            body += buffer
        buffer = input() + '\n'

        # Transmet ces informations avec l'entête `EMAIL_SENDING`.
        email = json.dumps(gloutils.GloMessage(
            header=gloutils.Headers.EMAIL_SENDING,
            payload=gloutils.EmailPayload(
                destination=destination,
                subject=subject,
                body=body
            )))




    def _check_stats(self) -> None:
        """
        Demande les statistiques au serveur avec l'entête `STATS_REQUEST`.

        Affiche les statistiques à l'aide du gabarit `STATS_DISPLAY`.
        """
        request = json.dumps(gloutils.GloMessage(
            header=gloutils.Headers.STATS_REQUEST
        ))
        glosocket.send_msg(self._socket, request)
        reply = json.loads(glosocket.recv_msg(self._socket))
        print(gloutils.STATS_DISPLAY.format(count=reply["count"], size=reply["size"]))


    def _logout(self) -> None:
        """
        Préviens le serveur avec l'entête `AUTH_LOGOUT`.

        Met à jour l'attribut `_username`.
        """
        logout_msg = json.dumps(gloutils.GloMessage(
            header=gloutils.Headers.AUTH_LOGOUT,
        ))
        glosocket.send_msg(self._socket, logout_msg)
        self._username = ""

    def run(self) -> None:
        """Point d'entrée du client."""
        should_quit = False

        while not should_quit:
            if not self._username:
                # Authentication menu
                pass
            else:
                # Main menu
                pass


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--destination", action="store",
                        dest="dest", required=True,
                        help="Adresse IP/URL du serveur.")
    args = parser.parse_args(sys.argv[1:])
    client = Client(args.dest)
    client.run()
    return 0


if __name__ == '__main__':
    sys.exit(_main())
