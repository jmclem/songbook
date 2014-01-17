#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import fnmatch
import os

def recursiveFind(root_directory, pattern):
    matches = []
    for root, dirnames, filenames in os.walk(root_directory):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches

def split_author_names(string):
    """Split author between first and last name.

    The last space separates first and last name, but spaces following a
    backslash or a command are not separators.
    Examples:
    - Edgar Allan Poe => Poe, Edgar Allan
    - Edgar Allan \emph {Poe} => \emph {Poe}, Edgar Allan
    - The Rolling\ Stones => Rolling\ Stones, The
    - The {Rolling Stones} => {Rolling Stones}, The
    """
    ignore_space = False
    last_space = index = 0
    brace_count = 0
    for char in string:
        index += 1
        if brace_count == 0:
            if char == "\\":
                ignore_space = True
            elif not char.isalnum() and ignore_space:
                ignore_space = False
            elif char == " ":
                last_space = index
        if char == "}":
            brace_count += 1
        if char == "{":
            brace_count -= 1
    return string[:last_space], string[last_space:]

def split_sep_author(string, sep):
    authors = []
    match = sep.match(string)
    while match:
        authors.append(match.group(2))
        string = match.group(1)
        match = sep.match(string)
    authors.append(string)
    return authors

def processauthors(authors_string, after = [], ignore = [], sep = []):
    """Return a list of authors

    For example, we are processing:
    # processauthors(
    #   "Lyrics by William Blake (from Milton, 1808), music by Hubert Parry (1916), and sung by The Royal\ Choir~of~Nowhere (just here to show you how processing is done)",
    #   after = ["by"],
    #   ignore = ["anonymous"],
    #   sep = ["and"]
    #   )

    The "authors_string" string is processed as:

    1) First, parenthesis (and its content) are removed.
    # "Lyrics by William Blake, music by Hubert Parry, and sung by The Royal\ Choir~of~Nowhere"

    2) String is split, separators being comma and words from "sep".
    # ["Lyrics by William Blake", "music by Hubert Parry", "sung by The Royal\ Choir~of~Nowhere"]

    3) Everything before words in "after" is removed.
    # ["William Blake", "Hubert Parry", "The Royal\ Choir~of~Nowhere"]

    4) Strings containing words of "ignore" are dropped.
    # ["William Blake", "Hubert Parry", The Royal\ Choir~of~Nowhere"]

    5) First names are moved after last names
    # ["Blake, William", "Parry, Hubert", Royal\ Choir~of~Nowhere, The"]
    """

    # Removing parentheses
    opening = 0
    dest = ""
    for char in authors_string:
        if char == '(':
            opening += 1
        elif char == ')' and opening > 0:
            opening -= 1
        elif opening == 0:
            dest += char
    authors_string = dest

    # Splitting strings
    authors_list = [authors_string]
    for sepword in sep:
        dest = []
        for author in authors_list:
            dest.extend(split_sep_author(author, sepword))
        authors_list = dest

    # Removing stuff before "after"
    dest = []
    for author in authors_list:
        for afterword in after:
            match = afterword.match(author)
            if match:
                author = match.group(1)
                break
        dest.append(author)
    authors_list = dest

    # Ignoring ignored authors
    dest = []
    for author in authors_list:
        ignored = False
        for ignoreword in ignore:
            if author.find(str(ignoreword)) != -1:
                ignored = True
                break
        if not ignored:
            dest.append(author)
    authors_list = dest

    # Cleaning: removing empty authors and unnecessary spaces
    authors_list = [author.lstrip() for author in authors_list if author.lstrip()]

    # Moving first names after last names
    dest = []
    for author in authors_list:
        first, last = split_author_names(author)
        if first:
            dest.append("%(last)s, %(first)s" % {
                'first': first.lstrip(),
                'last': last.lstrip(),
                })
        else:
            dest.append(last.lstrip())
    authors_list = dest

    return authors_list
