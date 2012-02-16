# -*- coding: utf-8 -*- 

""" 
   Choisit un nombre entre 0 et 100 et demande à l'utilisateur 
   de le deviner, en lui donnant à chaque fois une indication : sa réponse
   est elle plus grande ou plus petite que le nombre à deviner.

   Le jeu maintient un compteur qui permettra au joueur de connaitre sa 
   performance à la fin de la partie.
""" 

# import d'un module de la bibliothèque standard 
import random 

# nombre entre 0 et 100 au hasard 
nombre = random.randint(0, 100) 
reponse = None # None est ce qu'il y a de plus proche de 'null' 

compteur = 0 # definition d'un entier
tentatives = [] # definition d'une liste
victoire = False
conditions_de_sortie = (nombre, 'quitter')

print ("J'ai un nombre en tête, essayez de le deviner "
       "(ou entrez 'quitter' pour abandonner la partie)")

# la boucle while est rarement utilisée
while reponse not in conditions_de_sortie: 

    compteur += 1 # incrémentation. Il n'y a pas de d'instruction ++ 
    reponse_telle_quelle = raw_input('Choississez un nombre entre 0 et 100:\n')
    reponse = reponse_telle_quelle.strip().lower()
    tentatives.append(reponse)

    # python est dynamiquement typé, mais fortement typé 
    # on doit parfois transtyper ses valeurs 
    try: 
        reponse = int(reponse) 
        assert 0 <= reponse <= 100 # lève une exception si  faux 

    # les exceptions sont massivement utilisées y compris là 
    # où vous utiliseriez des operations conditionelles 
    except (ValueError, AssertionError): 
        if reponse != 'quitter':
            print "'%s' n'est pas un nombre entre 0 et 100" % reponse_telle_quelle 
            continue # sauter au prochain tour de boucle 

    if reponse < nombre: 
        print 'Le nombre est plus grand que "%s"' % reponse 

    elif reponse > nombre: 
        print 'Le nombre est plus petit que "%s"' % reponse 

    else:
        victoire = True

if victoire:
    # on peut utiliser un mapping pour le formattage de chaîne 
    print 'Vous avez trouvé "%(nombre)s" en %(compteur)s coups:' % { 
            'nombre': nombre, 'compteur': compteur }

    # la boucle for est très courrante en Python
    # et elle ne demande aucune forme de compteur
    for nombre in tentatives:
        print '\t - %s' % nombre

print "Au revoir"