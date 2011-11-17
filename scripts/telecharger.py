#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


"""
    Ce script attend une serie d'URLs en paramètre et va télécharger les
    ressources en ligne pour les sauvegarder dans le répertoire courant.
    
    usage:
        telecharger.py http://www.google.com http://wikipedia.fr  
"""


import os
import sys
import urllib2
import urlparse


# il n'est pas rare de créer ses propres exceptions
# ne serait-ce que par facilité
# on définit une classe, et on hérite de la classe exception
class ErreurDeTelechargement(Exception):
    """
        Les classes aussi peuvent être documentée par des docstrings.
    """
    pass # ferme un bloc vide


# une fonction avec deux paramètres obligatoires et un paramètre 
# optionel avec une valeur par défaut
def telecharger(url, dossier, taille_max=100000000):
    """
        Les docstrings sont aussi très utiles pour documenter des fonctions.
    """
    
    # python vient avec des modules qui permettent d'analyser une URL
    # ou de créer de chemin de fichier de manière multi plateforme
    nom_de_domaine = urlparse.urlsplit(url).netloc
    chemin = os.path.join(dossier, nom_de_domaine + '.dump')

    try:
        ressource = urllib2.urlopen(url) # ouvrir la ressource en ligne
    except (urllib2.URLError, ValueError):
        erreur = "Impossible de d'acceder à l'adresse '%s'" % url
        raise ErreurDeTelechargement(erreur)

    try:
        fichier = open(chemin, 'w') # ouvrir un fichier en écriture
        fichier.write(ressource.read(taille_max)) # on écrit
        fichier.close() # toujours fermer le fichier
    except (OSError, IOError):
        erreur = 'Impossible de sauvegarder "%s" dans le fichier "%s"' % (
                url, chemin)
        raise ErreurDeTelechargement(erreur)

    return chemin


# ceci est une astuce pour permettre au code qui vient après de ne 
# s'éxécuter que si le script est appelé directement
# il ne s'éxécutera pas si le script est importé
if __name__ == "__main__":

    erreurs = [] # liste vide
    fichiers = {} # dictionnaire (mapping) vide
    # __file__ est le chemin vers le script courant
    dossier_du_script = os.path.dirname(os.path.abspath(__file__))

    # les paramètres passés à un script sont accessibles dans sys.argv
    # sous forme de liste dont le premier argument est le nom du script
    urls = sys.argv[1:] # on retire le premier argument

    # une liste vide est consédérée comme "fausse" dans un contexte booléen
    if not urls:
        print 'Vous devez passer au moins une URL en paramètre'
        sys.exit(1) # sortie du script en retournant le code '1'

    # la boucle 'for' itère automatiquement sur les sequences
    for url in urls:
        try:
            fichiers[url] = telecharger(url, dossier_du_script)
        except ErreurDeTelechargement as e:
            erreurs.append(e.message)

    if erreurs:
      # len() donne la taille de n'importe quelle séquence
      print 'Il y a eu %s erreur(s) pendant le téléchargement:' % len(erreurs)
      for erreur in erreurs:
          print '\t - %s' % erreur # '\t' insère une tabulation

    if fichiers:
      print 'Les fichiers suivant on été téléchargés :'
      # on peut itérer sur des paires d'objets
      for url, fichier in fichiers.items():
          print '\t - %s => %s' % (url, fichier)
