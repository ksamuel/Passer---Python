#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import urllib2
import json
from collections import Counter
from contextlib import closing


class ParseurTwitter(object):
    """
        Télécharge les derniers tweets dans une langue, et
        récupère les mots pour déterminer ceux qui sont les plus
        utilisés.
    """

    # on définit quelques variables de classes (tout ce qui est
    # plus ou moins statique dans notre code)

    # nombre de mots qu'on veut récupérer de twitter par défaut
    mots_max = 1000000
    # la source des mots depuis twitter
    url_source = "http://search.twitter.com/search.json"
    # la requête GET qu'on vas demander à la source
    requete = "?lang=%s&q=*&result_type=recent"
    # le nombre d'essai qu'on va faire si la source ne répond pas
    essais_max = 3
    # la taille minimale d'un mot qu'on souhaite compter
    taille_mot_min = 3
    # les mots qu'on ne souhaite pas compter, comme les prépositions
    # communes, etc
    mots_vides = set(("les", "est", "pas", "que", "pour", "qui",
                       "avec", "une", "follow", "des", "sur",
                       "mais", "dans", "tre"))


    # initlisatation de notre classe
    # essentiellement le passage en argument de la langue et
    # la création du compteur
    def __init__(self, langue):
        self.langue = langue
        self.compteur = Counter()


    def telecharger_tweets(self):
        """
            Télécharge les tweets, et permet d'itérer sur chaque
            tweet.
        """

        # on créé la première url avec le source, la requete GET
        # et la lanque
        url_suivante = self.url_source + (self.requete % self.langue)
        essais = 0

        # tant qu'il y a encore une page de lire, on continue
        # c'est presque une boucle infinie, car il est peut probable
        # que vous arriviez au bout de tweeter avec votre laptop
        while url_suivante:

            # on ouvre une connection sur l'url comme on ouvrirait
            # un fichier. l'utilisation du context manager "closing"
            # nous permet d'utiliser le mot clé with
            with closing(urllib2.urlopen(url_suivante)) as connection:

                # le mot clé with ne nous dispense pas de gérer
                # les erreurs, et il y en un a un paquets possibles
                # quand on travail en réseau, tout le code
                # est donc enrobé dans un try / except
                try:
                    # on essaye de récupérer le contenu situé à l'url
                    reponse = connection.read(20000)
                    # les données sont normalement au format JSON
                    # que Python sait parser nativement
                    # on transforme donc le JSON en une imbrications
                    # de listes et de dictionnaires
                    donnees_json = json.loads(reponse)
                    # twitter renvoit toujours la page suivante si
                    # elle existe car il expose une API REST
                    # donc on fabrique l'url suivante grace à la valeur
                    # qu'il nous donne
                    url_suivante = self.url_source + donnees_json['next_page']
                    essais = 0
                except (KeyError, TypeError):
                    # Si la ligne créant "url_suivante" n'a pas marché
                    # c'est qu'on arrive à la fin du flux
                    # donc on sort de la boucle
                    url_suivante = None
                except urllib2.URLError:
                    # url invalide, pas de connection internet, etc
                    # on sort du programme
                    sys.exit("Impossible d'accéder à l'url : %s. "
                             "Verifiez l'adresse et votre connection"
                             " internet." % url_suivante)
                except urllib2.HTTPError as e:
                    # le server en face répond un erreur
                    # c'est peut être temporaire, on réessaye
                    if essais >= self.essais_max:
                        sys.exit("Echec à la récupération de "
                                 "l'url : %s" % url_suivante)
                    essais += 1
                    print "Http Error (%s) for URL: %s" % (
                           e.code, url_suivante)
                    print "Server answered: %s" % e.msg
                    print "Retry..."

                else:
                    # si tout s'est bien passé, on retourne le
                    # texte des tweets avec yield pour donner
                    # une l'impression de simplement itérer sur
                    # une collection de tweets
                    for tweet in donnees_json['results']:
                        yield tweet['text']


    def lister_les_mots(self, tweets, mots_max):
        """
            Prend un itérable de tweets en paramètre et
            le transforme en un itérable de mots, limités en nombre par
            mots_max.
        """

        # on split juste le tweet et on yield chaque mot
        # avec un limite
        # ça va permettre de s'arrêter à un certains nombre de mots
        # malgré le fait que telecharger_tweets est une source
        # presque infinie de tweets
        i = 0
        while i < mots_max:
            for x in tweets.next().split():
                yield x
                i += 1


    def nettoyer_tweet(self, text):
        """
            Prends un tweet et retire tout ce qui n'est pas intéressant
            à compter, comme les mentions, les tags ou les urls.

            On retire aussi la ponctuation et les chiffres arabes.
        """

        text = text.strip().lower()
        # retirer les @user, $company et #tags
        text = re.sub(r'(?:^|\s)(?:@|#|\$)[^\s]+(?:\s|$)', ' ', text)
        # returer les http//:truc
        text = re.sub(r'(?:^|\s)http://[^\s]+(?:\s|$)', ' ', text)
        # retirer les !, ?, 1-9, /, :, etc
        return re.sub(r'[^a-z\-]', ' ', text)


    def filtrer_un_mot(self, word):
        """
            Retourne True si le mot doit être compté, False
            sinon. Pour le moment, vérifie la taille minimale et
            si il fait parti de la liste de mots vides.
        """
        return len(word) >= self.taille_mot_min and word not in self.mots_vides


    def count(self, mots_max=None):
        """
            Lance le téléchargement et le comptage des mots,
            et retourne le résultat.
        """

        # on créé un générateur (donc un itérable) qui prend les
        # tweets et les nettoient
        tweets = (self.nettoyer_tweet(tweet) for tweet in self.telecharger_tweets())
        # on passe cet itérable au listeur de mot, en lui passant
        # une limite de mots
        words = self.lister_les_mots(tweets, mots_max or self.mots_max)
        # lister_les_mots retourne aussi un générateurs, que l'on
        # filtre pour récupérer uniquement les mots utiles
        filtered_words = (word for word in words if self.filtrer_un_mot(word))
        # enfin on passe cet itérable au compteur, qui fait sont travail
        # en compteur l'occurence de chaque élément
        self.compteur.update(filtered_words)
        # et on retourne le compteur
        return self.compteur


if __name__ == "__main__":
    resultats = ParseurTwitter('fr').count()
    # on affiche les 100 mots les plus communs
    for word, score in resultats.most_common(100):
        print "%s: %s" % (word, score)


