"""\
GLO-2000 Travail pratique 4 - Client
Noms et numéros étudiants:
-Jérémy Doiron (536895119)
-Yao Zu (536770891)
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
        username = input("Entrez votre nom d'utilisateur: ")
        password = getpass.getpass("Entrez votre mot de passe: ")
        if (username and password):
            register_request = json.dumps(gloutils.GloMessage(
                header=gloutils.Headers.AUTH_REGISTER,
                payload=gloutils.AuthPayload(
                    username=username,
                    password=password
            )))
            glosocket.send_msg(self._socket, register_request)
            reply = json.loads(glosocket.recv_msg(self._socket))
            if (reply["header"] == gloutils.Headers.OK):
                self._username = username
            elif (reply["header"] == gloutils.Headers.ERROR):
                print(reply["payload"])
        else:
            print("""La création a échouée:
 - Le nom d'utilisateur est invalide.
 - Le mot de passe n'est pas assez sûr.""")


    def _login(self) -> None:
        """
        Demande un nom d'utilisateur et un mot de passe et les transmet au
        serveur avec l'entête `AUTH_LOGIN`.

        Si la connexion est effectuée avec succès, l'attribut `_username`
        est mis à jour, sinon l'erreur est affichée.
        """
        username = input("Entrez votre nom d'utilisateur: ")
        password = getpass.getpass("Entrez votre mot de passe: ")
        if(username and password):
            login_request = json.dumps(gloutils.GloMessage(
                header=gloutils.Headers.AUTH_LOGIN,
                payload=gloutils.AuthPayload(
                    username=username,
                    password=password
                )))
            glosocket.send_msg(self._socket, login_request)
            reply = json.loads(glosocket.recv_msg(self._socket))
            if (reply["header"] == gloutils.Headers.OK):
                self._username = username
            elif (reply["header"] == gloutils.Headers.ERROR):
                print(reply["payload"])
        else:
            print("Nom d'utilisateur ou mot de passe invalide.")


    def _quit(self) -> None:
        """
        Préviens le serveur de la déconnexion avec l'entête `BYE` et ferme le
        socket du client.
        """
        quit_msg = json.dumps(gloutils.GloMessage(
            header=gloutils.Headers.BYE
        ))
        glosocket.send_msg(self._socket, quit_msg)
        self._socket.close()


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
        read_request = json.dumps(gloutils.GloMessage(
            header=gloutils.Headers.INBOX_READING_REQUEST
        ))
        glosocket.send_msg(self._socket, read_request)
        read_reply = json.loads(glosocket.recv_msg(self._socket))
        if (read_reply["header"] == gloutils.Headers.OK):
            if (read_reply["payload"] == []):  # TODO: test
                print("Aucun courriel à lire")
                return
            else:
                for email in read_reply["payload"]:
                    print(email)
                choice = int(input(f"Entrez votre choix [1-{len(email)}]: "))
                choice_request = json.dumps(gloutils.GloMessage(
                    header=gloutils.Headers.INBOX_READING_CHOICE,
                    payload=gloutils.EmailChoicePayload(
                        choice=choice
                )))
                glosocket.send_msg(self._socket, choice_request)
                email_reply = json.loads(glosocket.recv_msg(self._socket))
                if (email_reply["header"] == gloutils.Headers.OK):
                    gloutils.EMAIL_DISPLAY.format(sender=email_reply["payload"]["sender"], to=email_reply["payload"]["destination"], subject=email_reply["payload"]["subject"], date=email_reply["payload"]["date"], body=email_reply["payload"]["content"])


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
        destination = input("Entrez l'adresse du destinataire: ")
        subject = input("Entrez le sujet: ")
        
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
            payload=gloutils.EmailContentPayload(
                sender="",  # TODO:...
                destination=destination,
                subject=subject,
                date=gloutils.get_current_utc_time(),
                content=body
        )))
        reply = json.loads(glosocket.recv_msg(self._socket))
        if (reply["header"] == gloutils.Headers.OK):
            print("Envoi avec succès") 
        elif (reply["header"] == gloutils.Headers.ERROR):
            print(reply["payload"])


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
        if (reply["header"] == gloutils.Headers.OK):
            print(gloutils.STATS_DISPLAY.format(count=reply["payload"]["count"], size=reply["payload"]["size"]))
        elif (reply["header"] == gloutils.Headers.ERROR):
            print(reply["payload"])


    def _logout(self) -> None:
        """
        Préviens le serveur avec l'entête `AUTH_LOGOUT`.

        Met à jour l'attribut `_username`.
        """
        logout_msg = json.dumps(gloutils.GloMessage(
            header=gloutils.Headers.AUTH_LOGOUT
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
