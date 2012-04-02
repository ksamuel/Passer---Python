#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


"""
    Télécharge la liste des 100 questions et réponses
    les mieux notées sur stackoverflow,
    et créé depuis le CSV une liste de liens vers ces questions, puis
    les formatent sous forme de tableau tableau HTML afin de les poster
    facilement sur un blog.
"""

import csv
import urllib
import tempfile
from itertools import islice


def creer_url(patron, *args, **kwargs):
    """
        Fabrique une url à partir d'un patron d'url et de n'importe quel
        argument passé en paramettre
    """
    if args:
        patron = patron % args
    if kwargs:
        patron = patron % kwargs
    return patron


def extraire(url_du_csv, patron,
             slugifier=lambda s: '-'.join(s.strip().lower().split())):
    """
        Télécharge les données, et retourne un générateur dont la sortie
        contient le score, l'id, le titre et l'url de chaque question.
    """

    temp = tempfile.NamedTemporaryFile().name # créer un fichier temporaire
    urllib.urlretrieve(url_du_csv, temp) # télécharger le CSV

    fichier = open(temp):

    lignes = csv.reader(fichier) # parser le CSV téléchargé

    # itérer sur les lignes du csv, sauf la première
    for score, ID, titre in islice(lignes, 1, None):
        # créer l'url de la question, puis mettre en sortie
        # le score, l'id, le titre et l'url de chaque question
        url = creer_url(patron, id=ID, slug=slugifier(titre))
        yield score, ID, titre, url

    fichier.close()


# cette partie de ne s'exécute pas en cas d'import
if __name__ == '__main__':

    # squelette d'une URL de question sur stackoverflow
    patron = "http://stackoverflow.com/questions/%(id)s/%(slug)s"

    # début d'un fichier HTML 5
    print """
    <html>
    <head>
        <meta charset="utf-8">
        <title>Analyse du tag Python sur stackoverflow</title>
    </head>
    <table>
    <h1>Analyse du tag Python sur stackoverflow</h1>
    <caption>Top 100 des questions sur Python sur Stackoverflow</caption>
    <thead>
        <tr>
            <th>Score</th>
            <th>Titre</th>
        </tr>
    </thead>
    <tbody>
    """

    # Affichage du premier tableau
    source = 'http://data.stackexchange.com/StackOverflow/csv/70024'

    for score, ID, titre, url in extraire(source, patron):

        print "<tr>"
        print "<td>%s</td>" % score
        print "<td><a href='%s'>%s</a></td>" % (url, titre)
        print "</tr>"

    print """
    </tbody>
    </table>
    """

    # Affichage du second tableau
    print """
    <table>
    <caption>Top 100 des réponses sur Python sur Stackoverflow</caption>
    <thead>
        <tr>
            <th>Score</th>
            <th>Titre</th>
        </tr>
    </thead>
    <tbody>
    """

    source = 'http://data.stackexchange.com/StackOverflow/csv/70039'

    for score, ID, titre, url in extraire(source, patron):

        print "<tr>"
        print "<td>%s</td>" % score
        print "<td><a href='%s'>%s</a></td>" % (url, titre)
        print "</tr>"

    print """
    </tbody>
    </table>
    </html>
    """