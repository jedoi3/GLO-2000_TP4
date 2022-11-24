"""\
GLO-2000 Travail pratique 4 - Serveur
Noms et numéros étudiants:
-Jérémy Doiron (536895119)
-Yao Zu (536770891)
-
"""

from email.message import EmailMessage
import hashlib
import hmac
import json
import os
import select
import smtplib
import socket
import sys

import glosocket
import gloutils


class Server:
    """Serveur mail @glo2000.ca."""

    def __init__(self) -> None:
        """
        Prépare le socket du serveur `_server_socket`
        et le met en mode écoute.

        Prépare les attributs suivants:
        - `_client_socs` une liste des sockets clients.
        - `_logged_users` un dictionnaire associant chaque
            socket client à un nom d'utilisateur.

        S'assure que les dossiers de données du serveur existent.
        """
        # self._server_socket
        # self._client_socs
        # self._logged_users
        # ...

        #Prépare le socket du serveur `_server_socket` et le met en mode écoute.
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((gloutils.SERVER_HOST, gloutils.SERVER_PORT))
        self._server_socket.listen()
        print(f"Listening on port {self._server_socket.getsockname()[1]}")
        return self._server_socket

        #Prépare les attributs suivants:
        self._client_socs = []
        self._logged_users = {}
        self._logged_users[client_soc] = username

    def cleanup(self) -> None:
        """Ferme toutes les connexions résiduelles."""
        for client_soc in self._client_socs:
            client_soc.close()
        self._server_socket.close()

    def _accept_client(self) -> None:
        """Accepte un nouveau client."""

        client_socket, _ = self.server_socket.accept()
        # self._client_list.append(client_socket)


    def _remove_client(self, client_soc: socket.socket) -> None:
        """Retire le client des structures de données et ferme sa connexion."""

        try:
            message = glosocket.recv_msg(client_soc)
        # Si le client s'est déconnecté, on le retire de la liste.
        except glosocket.GLOSocketError:
            #_remove_client_from_list(client_socket)
            self.remove(client_soc)
            client_soc.close()
            return


    def _create_account(self, client_soc: socket.socket,
                        payload: gloutils.AuthPayload
                        ) -> gloutils.GloMessage:
        """
        Crée un compte à partir des données du payload.

        Si les identifiants sont valides, créee le dossier de l'utilisateur,
        associe le socket au nouvel l'utilisateur et retourne un succès,
        sinon retourne un message d'erreur.
        """
        # Crée un compte à partir des données du payload.

        return gloutils.GloMessage()

    def _login(self, client_soc: socket.socket, payload: gloutils.AuthPayload
               ) -> gloutils.GloMessage:
        """
        Vérifie que les données fournies correspondent à un compte existant.

        Si les identifiants sont valides, associe le socket à l'utilisateur et
        retourne un succès, sinon retourne un message d'erreur.
        """
        succes=False
        error_message = "Une erreur est survenue."
        # Vérifie que les données fournies correspondent à un compte existant.
        if payload.username in self._logged_users:
            succes=True
            self._logged_users[client_soc] = payload.username
        else:
            succes=error_message
            return gloutils.GloMessage(succes)


    def _logout(self, client_soc: socket.socket) -> None:
        """Déconnecte un utilisateur."""






    def _get_email_list(self, client_soc: socket.socket
                        ) -> gloutils.GloMessage:
        """
        Récupère la liste des courriels de l'utilisateur associé au socket.
        Les éléments de la liste sont construits à l'aide du gabarit
        SUBJECT_DISPLAY et sont ordonnés du plus récent au plus ancien.

        Une absence de courriel n'est pas une erreur, mais une liste vide.
        """
        email_list = gloutils.EmailListPayload()

        if (email_list != []):
            for i in range(len(email_list)):
                email_list[i]=gloutils.SUBJECT_DISPLAY.format(number=i, subject=email_list[i])
        else:
            return gloutils.GloMessage(email_list)
        return gloutils.GloMessage(email_list)

    def _get_email(self, client_soc: socket.socket,
                   payload: gloutils.EmailChoicePayload
                   ) -> gloutils.GloMessage:
        """
        Récupère le contenu de l'email dans le dossier de l'utilisateur associé
        au socket.
        """

        data= glosocket._recvall(client_soc, payload)

        return gloutils.GloMessage(data)

    def _get_stats(self, client_soc: socket.socket) -> gloutils.GloMessage:
        """
        Récupère le nombre de courriels et la taille du dossier et des fichiers
        de l'utilisateur associé au socket.
        """
        # Récupère le nombre de courriels
        length = len(self._get_email_list(client_soc))
        size= os.path.getsize(self._get_email_list(client_soc))
        gloutils.STATS_DISPLAY.format(number=length, size=size)

        return gloutils.GloMessage(STATS_DISPLAY)

    def _send_email(self, payload: gloutils.EmailContentPayload
                    ) -> gloutils.GloMessage:
        """
        Détermine si l'envoi est interne ou externe et:
        - Si l'envoi est interne, écris le message tel quel dans le dossier
        du destinataire.
        - Si le destinataire n'existe pas, place le message dans le dossier
        SERVER_LOST_DIR et considère l'envoi comme un échec.
        - Si le destinataire est externe, transforme le message en
        EmailMessage et utilise le serveur SMTP pour le relayer.

        Retourne un messange indiquant le succès ou l'échec de l'opération.
        """

        # send email et Détermine si l'envoi est interne ou externe

        # succes de l'envoi
        succes=False


        if payload.recipient in self._logged_users.values():
            # écris le message tel quel dans le dossier du destinataire.
            gloutils.write_email(payload.recipient, payload.subject, payload.body)
            succes=True
        elif payload.recipient not in self._logged_users.values():
            # transforme le message en EmailMessage et utilise le serveur SMTP pour le relayer.
            msg = EmailMessage()
            msg['Subject'] = payload.subject
            msg['From'] = gloutils.SERVER_EMAIL
            msg['To'] = payload.recipient
            msg.set_content(payload.body)
            with smtplib.SMTP_SSL(gloutils.SERVER_SMTP, gloutils.SERVER_SMTP_PORT) as smtp:
                smtp.login(gloutils.SERVER_EMAIL, gloutils.SERVER_PASSWORD)
                smtp.send_message(msg)
                succes=True
        else:
            # place le message dans le dossier SERVER_LOST_DIR et considère l'envoi comme un échec.
            gloutils.write_email(gloutils.SERVER_LOST_DIR, payload.subject, payload.body)


        return gloutils.GloMessage(succes)

    def run(self):
        """Point d'entrée du serveur."""
        waiters = []
        while True:
            # Select readable sockets
            for waiter in waiters:
                # Handle sockets
                pass


def _main() -> int:
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        server.cleanup()
    return 0


if __name__ == '__main__':
    sys.exit(_main())
