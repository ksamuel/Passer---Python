#!/usr/bin/env python
# -*- coding= UTF-8 -*-

__author__  = 'Kevin Samuel'
__version__ = '0.1' 


"""
Generator to list and filter files recursively in a dir.
""" 

import os


class FilesLister(object):
    """
        Retourne 
    """


    # la méthode spéciale __init__ est appelée automatiquement quand un objet
    # est créé. Elle peut être utilisée là où vous utiliseriez un constructeur
    def __init__(self, dir_path, only=(), exclude=(), recursive=True):
        # self, la référence à l'objet courant DOIT être déclaré explicitement
        # dans chaque méthode
        self.dir_path = dir_path
        self.cannot_open = set()
        self.only = self._clean_exts(only)
        self.exclude = self._clean_exts(exclude)
        self.recursive = recursive
    
    
    def __iter__(self):
        """
            Iterating on this object returns the file list generator.
        """
        return self.list_files(only=self.only, exclude=self.exclude,
                               recursive=self.recursive)    

    
    def _files_list_generator(self, dir_path, recursive=True):
        """
            Generate a list of files located in dir_path and its subdir.
            Save the list of unaccessed dirs in self.cannot_open.
        """
        
        
        for file_name in os.listdir(dir_path):
        
            file_path = os.path.abspath(os.path.join(dir_path, file_name))
            
            if os.path.isdir(file_path):
                if recursive:
                    try:
                        for file_path in self._files_list_generator(file_path):
                            yield file_path
                    except OSError:
                        self.cannot_open.add(file_path)
            else:
                yield file_path    
    
    
    
    def _white_list_filter(self, files=(), ext=()):
        """
            Return a generator that keeps the files matching the extensions.
        """
        
        for f in files:
            for e in ext:
                if f.endswith(e):
                    yield f
              
                    
    def _black_list_filter(self, files=(), ext=()):
        """
            Return a generator that exclude the files matching the extensions.
        """
        
        for f in files:
            if not any(f.endswith(e) for e in ext):
                yield f
     
     
    def _clean_exts(self, exts):
        """
            Strip the dot and the star from an extension.
        """
        return [ext.strip('*').strip('.') for ext in exts]

        
    def list_files(self, only=(), exclude=(), recursive=True):
        """
            List the files in the current directory recursively not, 
            with filters if required.
        """
        self.cannot_open = set()
        files = self._files_list_generator(self.dir_path, recursive=recursive) 
        
        if only:
            files = self._white_list_filter(files, self._clean_exts(only))
        if exclude:
            files = self._black_list_filter(files, self._clean_exts(exclude))
            
        return files
   
   

if __name__ == '__main__':

    pass