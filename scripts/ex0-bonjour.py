# -*- coding: utf-8 -*-

"""
    Ce script demande le nom et l'age de l'utilisateur, puis affiche un 
    message en conséquence.
"""
 
# déclaration des chaînes de caractères que l'on affichera à l'utilisateur
demander_nom = "Comment vous appelez-vous ?\n" 
demander_age = 'Quel age avez vous?\n' 

# demander a l'utilisateur une saisie 
nom = raw_input(demander_nom) 
age = raw_input(demander_age) 

# vérification de la présence du nom et de l'age
# affichage d'un message selon la présence ou non de l'age
if age != "" and nom == "": 
  print 'Bonjour anonyme' 
  print 'Vous avez ' + age + ' ans' 

elif nom and not age: 
  print 'Bonjour ' +  nom 
  print 'Nous ne connaissons pas votre age' 

elif not (nom or age): 
  print '''Bonjour anonyme, 
nous ne connaissons pas votre age'''

else: 
  # formatage avec plusieurs variables 
  print "Vous vous appelez %s et vous avez %s ans" % (nom, age)