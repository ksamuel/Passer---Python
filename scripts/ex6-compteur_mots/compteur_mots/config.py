#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


import sys

from tempfile import gettempdir

from path import path


# Récupérer le chemin absolu vers le fichier config.py
FICHIER_COURANT = path(__file__).realpath()
# Le convertir en unicode
FICHIER_COURANT = FICHIER_COURANT.decode(sys.getfilesystemencoding())
# Récupérer le chemin absolu vers le dossier courant
DOSSIER_COURANT = FICHIER_COURANT.parent
# Construire le chemin vers le dossier contenant les fichiers de mots vides
DOSSIER_MOTS_VIDES = DOSSIER_COURANT / u'mots_vides'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'fichier_temporaire': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': path(gettempdir()) / 'parseur_mots.log',
            'maxBytes': 2000000,
            'backupCount': 1
        },
    },
    'loggers': {
        'fichier': {
            'handlers': ['fichier_temporaire'],
            'propagate': True,
            'level': 'INFO',
        },
        'terminal': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
    }

}
