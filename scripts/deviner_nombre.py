#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

# ^ les trois lignes optionnelles ci-dessus sont importantes:
# - la première permet de traiter le script comme un éxécutable sous Unix
# - la seconde défini l'encodage et permet d'utiliser les accents dans le code
# - la dernière permet d'éditer facilement le code sous VI

"""
    Les chaînes de caractères définies par 3 '"' sont des chaînes multilignes.
    Python invite à autodocumenter son code en plaçant une chaîne de caractère
    comme première ligne de code: elle décrit le module courrant.
"""

# import d'un module de la bibliothèque standard
import random 

# nombre entre 1 et 100 au hasard
nombre = random.randint(0, 100)
reponse = None # None est ce qu'il y a de plus proche de 'null'

compteur = 0

while reponse != nombre: 

    compteur += 1 # incrémentation. Il n'y a pas de ++
    reponse = raw_input('Choississez un nombre entre 0 et 100:\n')

    # python est dynamiquement typé, mais fortément typé
    # on doit parfois caster ses valeurs
    try:
        reponse = int(reponse)
        assert 0 <= reponse <= 100 # déclenche une exception si c'est faux

    # les exceptions sont massivement utilisées
    # y compris là où vous utiliseriez des operations conditionelles
    except (ValueError, AssertionError):
         print "Vous devez rentrer un nombre entre 0 et 100, pas '%s'" % reponse
         continue # sauter au prochain tour de boucle

    if reponse < nombre:
        print 'Le nombre à trouver est plus grand que "%s"' % reponse

    if reponse > nombre:
        print 'Le nombre à trouver est plus petit que "%s"' % reponse

# on peut utiliser un mapping pour le formattage de chaîne
print 'Vous avez trouvé le nombre "%(nombre)s" en %(compteur)s coups' % {
        'nombre': nombre, 'compteur': compteur 
       }