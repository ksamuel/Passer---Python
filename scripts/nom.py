
# ceci est un commentaire

# l'absence d'accents est volontaire

# declaration de variable
##########################

# typage dynamique: pas besoin de le declarer
# ici on definit des chaines de caracteres
demander_nom = "Comment vous appelez-vous ?\n" # '\n' implique un saut de ligne
demander_age = 'Quel age avez vous?\n' # syntaxe avec "'" ...
repondre = """Vous vous appelez %s et vous avez %s ans""" # ... et avec '"""'

# demander a l'utilisateur une saisie
nom = raw_input(demander_nom)
age = raw_input(demander_age)

# logique conditionelle de base
###############################

# pas de parenthese ou de {}
# indentation obligatoire
if age and not nom: 
  print 'Bonjour anonyme'
  # formatage de chaine avec une variable
  print 'Vous avez %s ans' % age 

# elif condense else et if
elif nom and not age: # la negation utilise 'not', pas '!'
  print 'Bonjour %s' % nom
  print 'Nous ne connaissons pas votre age'

elif not (nom or age):
  print 'Bonjour anonyme, nous ne connaissons pas votre age'

else:
  # formatage avec plusieurs variables
  print repondre % (nom, age)

