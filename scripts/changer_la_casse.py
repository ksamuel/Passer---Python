#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4


"""
    Mets les extensions des fichiers d'un dossier en miniscule.
    Filtre par extension possible.
    Non récursif.
    
    usage:
        changer_casse.py /dossier/voulu [-e .ext,.ext]
"""



import os
import argparse
import glob


# création d'une classe: on hérite toujours par défaut de 'object'
class ChangeurDeCasse(object):
    """
        Liste les fichiers d'un dossier.
        Peut changer la casse de leur extension après.
    """

    # la méthode __init__ est appelée à la création d'un objet
    # on peut l'utiliser en lieu et place d'un constructeur
    # le reste ressemble exactement à une fonction
    def __init__(self, dossier, extension=None):
        # self, la référence à l'objet courant, doit être passé explicitement
        # pour toutes les methodes
        self.dossier = os.path.abspath(dossier)
        self.extensions = extension
        self.erreurs = []


    # méthode classique, sans paramètre
    def renommer(self):
        """
            Renomme les fichiers en mettant leurs extensions en minuscule
        """
        for fichier in self.fichiers:
            nom, ext = os.path.splitext(fichier) # assignation multiple
            nouveau_nom = nom + ext.lower() # extension en minuscule
            # gérer tout erreur d'écriture de fichier courantes
            try:
                os.rename(fichier, nouveau_nom)
            except (IOError, OSError):
                self.erreurs.append((fichier, 
                                     'Impossible de renommer le fichier'))

    
    # on peut demander à une méthode de se présenter comme un attribut
    # avec @property
    @property
    def fichiers(self):
        """
            Retourne la liste des fichiers du dossier, filtrée par extension.
        """
        # on peut itérer et filtrer en une ligne avec une syntaxe spéciale
        # appelée 'liste en intension'
        # ici on liste le contenu du dossier avec glob, puis on filtre
        # tout ce qui n'est pas un fichier
        contenu = os.path.join(self.dossier, '*') # motif pour glob()
        fichiers = (f for f in  glob.glob(contenu) if os.path.isfile(f))
        
        # si des extensions sous fournies, on filtre par extension
        if self.extensions:
            fichiers_filtres = []
            for fichier in fichiers:
                f = fichier.lower()
                # any() verify qu'il y a une valeur "vraie" dans une séquence
                # endswith() verifie si une chaine se termine par une autre
                if any((f.endswith(ext) for ext in self.extensions)):
                    fichiers_filtres.append(fichier)
            fichiers = fichiers_filtres

        return fichiers
         

if __name__ == '__main__':
    
    # Python vient avec le module 'argparse' qui permet de faire
    # des analyses d'arguments complexes: on définit les arguments attendus
    # et il retourne un conteneur avec leurs valeurs

    # __doc__ donne accès à la docstring du module
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dossier', 
                        help="Le chemin du dossier qu'il faut traiter")
    parser.add_argument('-e', dest='extensions', default='',
                        help="Une liste d'extensions pour filtrer les fichiers")
    args = parser.parse_args()

     # on transforme les extensions en liste
    extensions = args.extensions.split(',')

    # on instancie ChangeurDeCasse avec les paramètres passés en arguments
    changeur = ChangeurDeCasse(args.dossier, extensions)

    # 'fichier' à l'air d'être un attribut, mais c'est une méthode
    # décorée avec @property
    fichiers = changeur.fichiers

    print "Fichiers à modifier :"
    if fichiers:
        for fichier in fichiers:
            print '\t - %s' % fichier
    else:
        print 'Aucun'
    
    print 'Ces %s fichiers vont être renommés' % len(fichiers)

    confirmation = "Voulez-vous continuer ? (o/N)"
    reponse = raw_input(confirmation).lower()

    if reponse in ('y', 'o', 'yes', 'oui'):
        changeur.renommer()
        print 'Les fichiers on été renommés'
    