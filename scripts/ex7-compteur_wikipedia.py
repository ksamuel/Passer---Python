#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import re
import sys
import urllib2
import itertools

from collections import Counter
from contextlib import closing
import xml.etree.ElementTree as ET


class GestionnaireDeRedirection(urllib2.HTTPRedirectHandler):
    """
        Objet utilisé pour gérer un comportement personnalisé lorsque l'on
        rencontre une redirection HTTP.
    """


    def __init__(self, parser):
        self.parser = parser


    def http_error_301(self, req, fp, code, msg, headers):
        """
            Ajoute au parser l'url de la dernière redirection permanente
        """
        self.parser.url_de_secours = headers.get('location', None)
        return urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code,
                                                                msg, headers)


    def http_error_302(self, req, fp, code, msg, headers):
        """
            Ajoute au parser l'url de la dernière redirection temporaire
        """
        self.parser.url_de_secours = headers.get('location', None)
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code,
                                                                 msg, headers)


class ParseurWikipedia(object):
    """
        Télécharge des articles alétoirement dans une langue, et
        récupère les mots pour déterminer ceux qui sont les plus
        utilisés.
    """

    # nombre de mots qu'on veut récupérer de wikipedia par défaut
    mots_max = 1000000
    # la taille minimale d'un mot qu'on souhaite compter
    taille_mot_min = 3
    # le nombre d'essai qu'on va faire si la source ne répond pas
    essais_max = 3

    # une url à utiliser en cas d'erreur
    url_de_secours = ''

    # l'adresse de la page qui retourne un article au hasard
    # par langue (on a juste le franças ici pour l'exemple)
    urls_page_aleatoire = (
        ('fr',
         "https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard"),
    )

    # l'adresse qu'on vas utiliser pour lire l'article au format XML
    url_source = ("http://%s.wikipedia.org/w/api.php"
                 "?action=query&prop=revisions"
                 "&rvprop=content&format=xml&titles=%s")

    # les en-têtes que l'on va envoyer avec chaque requête HTTP
    # qui ici ne contient que le nom du navigateur que nous voulous simuler
    headers = (
      ('User-Agent',
       'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.12) '
       'Gecko/20080201 Firefox/2.0.0.12'),
    )

    # les mots qu'on ne souhaite pas compter, comme les prépositions
    # communes, etc. mais organiser par langue
    mots_vides = (
        ('fr',
         set(("les", "est", "pas", "que", "pour", "qui", "avec", "une",
             "des", "sur", "mais", "dans", "tre", "ref", 'www', 'par',
             'gorie', 'france', 'langue', 'date', 'ann', 'son', 'diteur',
             'ennann', 'align', 'taxobox', 'flagicon', 'com', 'http',
             'name', 'genre'))),
    )

    def __init__(self, langue, mots_vides=()):

        self.langue = langue
        self.mots_vides = set(mots_vides) or dict(self.mots_vides)[langue]
        self.compteur = Counter()
        self.headers = dict(self.headers)
        self.url_page_aleatoire = dict(self.urls_page_aleatoire)[langue]


    # methode appelée automatiquement quand on itère sur l'objet
    def __iter__(self):
        """
            Retourne des un générateur renvoyant des mots de wikipedia
        """
        articles = self.telecharger_les_articles()
        articles = (self.nettoyer_article(article) for article in self.telecharger_les_articles())
        mots = self.lister_les_mots(articles, self.mots_max)
        return (word for word in mots if self.filtre_les_mots(word))


    def filtre_les_mots(self, word):
        """
            Filtre les mots trop courts ou vides
        """
        return len(word) >= self.taille_mot_min and word not in self.mots_vides


    def compter(self, mots_max=None):
        """
            Retourne un compteur de fréquences des mots
        """
        self.compteur.update(itertools.islice(self, mots_max or self.mots_max))
        return self.compteur


    def lister_les_mots(self, articles):
        """
            Retourne un générateur qui divise les articles en mots
        """
        return (mot for article in articles for mot in article.split())



    def fail_or_retry(self, url, retry, exception):
        """
            Vérifie un compteur d'essais, et si il est dépassés, sort
            du script en affichant une erreur.

            Sinon, incrémente le compteur
        """

        if retry >= self.essais_max:
            sys.exit('Failed to fetch url: %s' % url)

        print "Http Error (%s) for URL: %s" % (exception.code, url)
        print "Server answered: %s" % exception
        print "Retry..."

        return retry + 1


    def telecharger_les_articles(self):
        """
            Télécharge les articles de wikipédia et retourne un générateur
            qui renvoit les articles un par un.
        """

        redirection_handler = GestionnaireDeRedirection(parser=self)
        url_opener = urllib2.build_opener(redirection_handler)
        requete_page_aleatoire = urllib2.Request(self.url_page_aleatoire,
                                                 headers=self.headers)

        retry = 0

        while True:

            # requête pour récupérer le nom d'un sujet aléatoirement
            try:
                with closing(url_opener.open(requete_page_aleatoire)) as reponse:
                    sujet_aleatoire = reponse.url.split('/')[-1]

            except (urllib2.HTTPError, urllib2.URLError) as e:
                # si on est dans un boucle infini, on récupère l'url de secours
                if getattr(e, 'msg', 'infinite loop'):
                    sujet_aleatoire = self.url_de_secours.split('/')[-1]
                else:
                    retry = self.fail_or_retry(requete_page_aleatoire, retry, e)

            try:

                # requête pour récupérer le contenu du sujet
                url_source = self.url_source % (self.langue, sujet_aleatoire)
                requete_du_sujet = urllib2.Request(url_source, headers=self.headers)

                with closing(url_opener.open(requete_du_sujet)) as reponse:

                    try:

                        # on transforme l'article en arbre xml
                        root = ET.fromstring(reponse.read(20000))

                        # et on fait une requête xpath pour récupérer
                        # uniquement le contenu
                        yield root.findall(".//*/rev")[0].text

                    except (IndexError, ET.ParseError):
                        # pas de texte pour cet article, ou un xml mal formé
                        # donc on passe au suivant
                        continue

                retry = 0

            except (urllib2.HTTPError, urllib2.URLError) as e:
                retry = self.fail_or_retry(url_source, retry, e)


    def nettoyer_article(self, text):
        """
            Nettoie les articles du contenu non significatif.
        """
        text = text.strip().lower()
        # on retire les tags wiki, les mots dedans ne sont pas significatifs
        text = re.sub(r'(?:^|\s)http://[^\s]+(?:\s|$)', ' ', text, flags=re.M)
        text = re.sub(r'[{}[\]|]{1,2}[^{}[\]|]*[{}[\]|]{1,2}', '', text, flags=re.M)
        return re.sub(r'[^a-z10-9\-]', ' ', text, flags=re.M)



results = ParseurWikipedia('fr').compter()
for word, score in results.most_common(100):
    print "%s: %s" % (word, score)
