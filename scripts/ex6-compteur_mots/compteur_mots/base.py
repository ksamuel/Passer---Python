#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import itertools

import urllib2
import json
from collections import Counter
from contextlib import closing


from logging import config, getLogger


import config


class BaseDeParseur(object):

    mots_max = 1000000
    essais_max = 3
    taille_mot_min = 3
    dossier_mots_vides = DOSSIER_COURANT / u'mots_vides'
    mots_vides = ()


    def __init__(self, langue, mots_vides=None,
                 logger='terminal', logging=config.LOGGING):

        self.langue = langue
        self.compteur = Counter()

        # Initialisation du logger
        config.dictConfig(logging)
        self.log = getLogger(logger)

        # On essaye de charger la liste des mots vides pour cette langue
        if mots_vides:
            self.mots_vides = mots_vides
        else:
            try:
                self.mots_vides = set(open(self.fichier_mot_vides(langue)))
            except (IOError, OSError):
                self.log.info(u"Aucun mots vides chargés")


    @classmethod
    def fichier_mot_vides(cls, langue):
        return config.DOSSIER_MOTS_VIDES / u'base_%s' % langue


    def __iter__(self):
        """
            Retourne des un générateur renvoyant des un flux de mots depuis
            la source de mots
        """
        morceaux = self.telecharger_les_morceaux()
        morceaux = (self.nettoyer_morceau(morceau) for morceau in morceaux)
        mots = self.lister_les_mots(morceaux, self.mots_max)
        return (word for word in mots if self.filtre_les_mots(word))


    def filtre_les_mots(self, mot):
        """
            Filtre les mots trop courts ou vides
        """
        return len(mot) >= self.taille_mot_min and mot not in self.mots_vides


    def compter(self, mots_max=None):
        """
            Retourne un compteur de fréquences des mots
        """
        self.compteur.update(itertools.islice(self, mots_max or self.mots_max))
        return self.compteur


    def lister_les_mots(self, morceaux):
        """
            Retourne un générateur qui divise les morceaux en mots
        """
        return (mot for morceau in morceaux for mot in morceau.split())


    def nettoyer_morceau(self, texte):
        """
            Prends un morceau et retire tout ce qui n'est pas intéressant
            à compter, comme la ponctuation, les chiffres arabes et les urls.

            On en profite pour normaliser la chaîne en minuscule et en retirant
            les caractères non ASCII.
        """

        texte = re.sub(r'(?:^|\s)http://[^\s]+(?:\s|$)', ' ', texte)

        # retirer les caractères non-ASCII, et si possible les remplacer
        # par un équivalent
        texte = unicodedata.normalize('NFKD', texte).encode('ascii', 'ignore')

        return re.sub(r'[^a-z\-]', ' ', texte)


    def count(self, mots_max=None):
        """
            Lance le téléchargement et le comptage des mots,
            et retourne le résultat.
        """

        morceaux = (self.nettoyer_morceau(morceau) for morceau in self.telecharger_morceaux())
        words = self.lister_les_mots(morceaux, mots_max or self.mots_max)
        filtered_words = (word for word in words if self.filtrer_un_mot(word))
        self.compteur.update(filtered_words)
        return self.compteur


if __name__ == "__main__":
    resultats = ParseurTwitter('fr').count()
    # on affiche les 100 mots les plus communs
    for word, score in resultats.most_common(100):
        print "%s: %s" % (word, score)


