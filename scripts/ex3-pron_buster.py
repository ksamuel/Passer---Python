#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from sqlite3 import connect
from itertools import islice

"""
    Analyse l'historique de Firefox pour voir combien de fois ont été
    visités des sites pornos.
"""

# on défini une fonction car nous allons réutiliser ce code plusieurs fois
# évidement, vous pouvez remplacer ces mots clés par des noms de domaines
# qui vous tiennent à coeur
def est_porno(domaine, mot_cles_porno=('sex', 'porn')):
    """
        18. Retourne True si `domain` contient un des mot clés porno.
    """
    for mot in mot_cles_porno:
        if mot in domaine:
            return True

# remplacez ici ce chemin d'historique par le votre
# firefox créé un fichier places.sqlite dans un dossier different pour
# chaque OS. Il va falloir chercher :-)
historique = '/User/.mozilla/firefox/01xwqr2a.default/places.sqlite'
connection = connect(historique)
curseur = connection.cursor()

# Le bon vieux SQL, toujours d'actualité
requete = """
    SELECT sites.rev_host as host, count(*) as visits
    FROM moz_historyvisits as visits,
         moz_places as sites
    WHERE  visits.place_id == sites.id
    GROUP BY host
    ORDER BY visits DESC
"""

resultats = curseur.execute(requete)

# on met les 10 sites les plus visités dans une liste à part
# le nom de domaine est inversé dans la base de donnée, on le remet dans l'ordre
# cette syntaxe est verbeuse
dix_premiers = resultats.fetchmany(10)
top_10_normal = []
for domaine, visites in dix_premiers:
    top_10_normal.append((domaine[-2::-1], visites))


# on cherche si il y a des sites pornographiques dans les 10 premiers sites
# avec une syntaxe plus courte
top_10_porno = [(dom, vis) for dom, vis in top_10_normal if est_porno(dom)]

# puis si il y en a dans tous les autres sites
# un code très condensé
domaines_porno = ((d[-2::-1], v) for d, v in resultats if est_porno(d[:1:-1]))
top_10_porno.extend(islice(domaines_porno, 10 - len(top_10_porno)))

# enfin on affiche tout ça
print "Top 10 sites normaux :"

for domaine, visites in top_10_normal:
    print u"\t - %s : visité %s fois" % (domaine, visites)

print "Top 10 porno :"

for domaine, visites in top_10_porno:
    print u"\t - %s : visité %s fois" % (domaine, visites)

# Sortie du programme :
# Top 10 sites normaux :
#      - 127.0.0.1 : visité 10317 fois
#      - duckduckgo.com : visité 9558 fois
#      - www.google.com : visité 8057 fois
#      - fr.wikipedia.com : visité 7083 fois
#      - stackoverflow.com : visité 5973 fois
#      - encrypted.google.com : visité 4751 fois
#      - github.com : visité 2665 fois
#      - mail.google.com : visité 2281 fois
#      - streambusters.com : visité 2170 fois
#      - yeleman.com : visité 1792 fois
# Top 10 porno :
#      - sitequicontientsex.com : visité 1 fois
#      - sitequicontientporn.com : visité 1 fois
