#!/usr/bin/env python
# -*- coding: utf-8 -*-


u"""
    Récupère les emails d'une boîte Gmail, et les filtres
    selon une expression rationelle. Affiche ensuite les résultats,
    et les sauvegarde optionellement dans un dossier au format mbox.
"""

import os
import re
import sys
import socket
import getpass
import imaplib
import argparse

from datetime import datetime
from email import message_from_string

# On définit les arguments que notre script va accepter

# Création du parseur d'arguments avec quelques settings d'ordre général
parser = argparse.ArgumentParser(description=__doc__)

# Ajout de quelques paramètres optionels
parser.add_argument('-p', '--password', nargs="?", type=str, default="",
                    help=u"Le mot de passe du compte")

parser.add_argument('-u', '--username', nargs="?", type=str, default="",
                    help=u"Le nom d'utilisateur du compte")


# Ajout d'un paramètre avec une vérification personalisées.
def dossier(chemin):
    if chemin and not os.path.isdir(chemin):
        message = u"%r: ce dossier n'existe pas" % chemin
        raise argparse.ArgumentTypeError(message)
    return chemin

parser.add_argument('-s', '--sauver-dans', nargs="?",
                    type=dossier, default='',
                    help=u"Si (et seulement si) spécifié, "
                         u"les emails seront téléchargés et sauvés "
                         u"dans ce dossier")

# Ajout d'un paramètre qui accepte une liste de valeurs
parser.add_argument('-d', '--dossiers', type=str, nargs='+',
                    default="tous", help=u"Les dossiers dans lesquels "
                                         u"chercher les mails.")

# Ajout de deux flags
parser.add_argument('-l', '--lister', action='store_true',
                     help=u"Liste les dossiers disponibles "
                          u"pour cette boîte")

parser.add_argument('-i', '--ignorer-la-casse', action='store_const',
                     default=0, const=re.I,
                     help=u"Ignore la différent majuscule/minuscule")

# Ajout d'un paramètre positionel
parser.add_argument('recherche', type=str,
                     nargs='?', default=".*",
                     help=u"Un texte ou une expression "
                          u"rationelle à chercher")

# On parse les arguments pour de bon
args = parser.parse_args()


# On se connecte au serveur IMAP de gmail
# On gère une éventuelle erreur de connection pour donner un message
# d'erreur qui a du sens à l'utilisateur final
try:
    connexion = imaplib.IMAP4_SSL("imap.gmail.com")
except socket.gaierror:
    sys.exit(u"Impossible de se connecter à gmail. Le serveur "
             u"est peut être inaccessible. Vérifiez que vous êtes bien "
             u"connecté à Internet, et réessayez plus tard")

# On récupère le nom d'utilisateur et le mot de passe, soit depuis
# les paramètres, soit depuis une invite de commande
# getpass s'assure que le mot de passe ne s'affiche pas en clair
username = args.username or raw_input(u"Entrez votre nom d'utilisateur : ")
password = args.password or getpass.getpass(u"Entrez votre mot de passe : ")

# On décode la saisie utilisateur, au cas où l'on soit sur une plateforme
# avec un encodage autre que utf8. On obtient ainsi de l'unicode.
encodage_du_terminal = sys.stdin.encoding or "utf8"
username = username.decode(encodage_du_terminal)
password = password.decode(encodage_du_terminal)
recherche = args.recherche.decode(encodage_du_terminal)

# On s'authentifie auprès de Gmail. Notez que l'on renvoit les identifiants
# au format utf8 et qu'on gère également le cas d'une mauvaise saisie
try:
    connexion.login(username.encode('utf8'), password.encode('utf8'))
except imaplib.IMAP4.error:
    sys.exit(u"Nom d'utilisateur ou mot de passe invalide")

# On récupère les différent dossiers de la boite mail
dossiers = [d.split('"')[-2] for d in connexion.list()[1]]

# Si on veut la liste des dossier, l'imprimer et sortir du script
if args.lister:
    print ', '.join(dossiers)
    sys.exit()

# Si on précise la liste des dossiers dans lesquels chercher,
# alors vérifier que chaque dossier spécificié existe bien, sans quoi
# il faut afficher une erreur.
if args.dossiers != 'tous':
    for dossier in args.dossiers:
        if dossier not in dossiers:
            sys.exit(u"%s n'existe pas dans cette boîte."
                     u" Les dossiers disponibles sont: %s" % (
                        dossier, ' ,'.join(dossiers)))
    dossiers = args.dossiers

# On récupère la date d'aujourd'hui pour l'utiliser plus tard
date_du_jour = datetime.now()

# On parcourt les dossiers un par un
for dossier in dossiers:

    connexion.select(dossier)

    # On demande la liste des tous les identifiants d'emails
    # Il est possible ici de filtrer pour avoir uniquement les emails lus,
    # répondus, à une certaine date, etc
    # Mais on va se contenter de tout récupérer. Si vous voulez aller plus
    # loin, voici les filtres:
    # http://www.example-code.com/csharp/imap-search-critera.asp
    reponse, identifiants = connexion.search(None, "ALL")

    # les identifiants sont retourner comme une seule chaîne, on en
    # fait une liste
    identifiants = identifiants[0].split()

    for identifiant in identifiants:

        # On télécharge l'email. "(RFC822)" veut dire "télécharger "
        # en entier mais on pourrait bien sûr télécharger juste
        # certaines metadonnés
        reponse, message = connexion.fetch(identifiant, "(RFC822)")

        # On extrait le contenu du message, et on le passe à un parseur
        # pour obtenir un bel objet email, facile à manipuler
        corps_du_message = message[0][1]
        email = message_from_string(corps_du_message)

        # On récupère l'encodage de l'email, et on décode les champs
        # From, To et Subject pour récupérer de l'unicode
        charset = email.get_content_charset() or 'utf8'
        auteur = email["From"].decode(charset, 'replace')
        destinataire = email["To"].decode(charset, 'replace')
        titre = email["Subject"].decode(charset, 'replace')

        # L'email est un format plus complexe qu'on le croit, il contient
        # des couches commes les oignons. Walk() nous permet de lister
        # toutes les couches, pour obtenir chaque partie de l'email.
        parties = tuple(email.walk())

        # Si il y a plus d'une partie, on le note
        suffix = len(parties) > 1

        # On boucle sur les parties, i étant le numéro de la partie,
        # et partie étant l'objet contenant toutes les données sur cette
        # partie
        for i, partie in enumerate(parties):

            # On vérifie le type de la partie. Si c'est "multipart",
            # alors c'est juste un conteneur, et on peut le sauter.
            # On vérifie également que le header 'Content-Disposition'
            # n'est pas présent, car il signalerait que cette partie
            # est une pièce jointe, ce dont nous n'avons pas besoin.
            if (partie.get_content_maintype() == 'multipart' or
                partie.get('Content-Disposition') is not None):
                continue

            # On récupère le contenu (le texte) de la partie
            # On demande à ce qu'il soit décodé pour obtenir de l'unicode
            texte = partie.get_payload(decode=True)

            # On recherche ce que demande l'utilisateur, ainsi que
            # quelques mots avant et après
            motif = ur'(.{0,30})(' + recherche + ur')(.{0,30})'
            resultat = re.search(motif, texte,
                                flags=args.ignorer_la_casse|re.U)

            # Si la recherche est concluante, on affiche de quoi
            # identifier l'email et le contenu trouvé.
            if resultat:

                print auteur, u'=>', destinataire, u':',\
                      titre, (("(Part %s)" % i) * suffix)

                if args.recherche != ".*":
                    print "..." + ''.join(resultat.groups()) + "..."

                # Si on doit sauvegarder l'email, on créé le nom du fichier
                # mbox à l'aide du nom du dossier et de la date du jour
                # et on écrit dedans
                if args.sauver_dans:

                    nom_de_fichier = "%s_%s.mbox" % (
                            dossier,
                            date_du_jour.strftime(u'%H:%M:%S_%d-%m-%Y')
                    )

                    chemin = os.path.join(args.sauver_dans,
                                         nom_de_fichier)

                    # On est en mode append, puisqu'on a un seul
                    # fichier mbox pour tous les mails de chaque dossier
                    # Notez qu'on peut simplifier ce code avec le mot
                    # clé "with" mais il est bon de démontrer un peu
                    # l'usage des exceptions
                    try:
                        f = open(chemin, 'a')
                    except (OSError, IOError) as e:
                        sys.exit(u"Impossible d'écrire dans '%s'. "
                                 u"Le système renvoit l'erreur: %s" % (
                                 chemin, e))
                    else:
                        try:
                            f.write(u"From %s\n" % auteur)
                            f.write(corps_du_message)
                            f.write("\n")
                        finally:
                            f.close()

                break

