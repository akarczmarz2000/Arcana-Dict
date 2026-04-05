# Arcana Dictionary – Version 0.3

## Overview

This project uses the existing Thuum canon as a structural foundation for an Arcana dictionary, search system, and translation tool.

It was developed in response to the closure of thuum.org to non-canon words. While that decision is understandable, it creates an opportunity to build a more flexible system, one that supports Arcana users in expanding and adapting the language.

The goal of this project is not only to provide search and translation tools, but also to bridge gaps in the Arcana dictionary where no direct words currently exist. Where necessary, the system will suggest alternatives based on similarity, synonym, or contextual meaning.

---

## Next Development Step
Alternate meanings are extracted from literal meanings in translator. First a word is turned into a token, this token is passed through the code to find any literal meaning matches. If there is a match then the code continues, otherwise it does not attempt an alternative search. The alternative word search takes the synonyms from the exact match and uses those as its search terms, looking for literal meaning of words only to match them against search terms. These terms are then returned and displayed under the header Alternative.

This means the level of searches are as follows:
- Literal meaning search: the program looks for any word matching the token.
- Synonym meaning search: the program looks at the synonyms held in the dictionary for each word searching for matches to the token.
- Interpretation meaning search: the program looks at the interpreatiuons held in the dictionary for each word searching for matches to the token.
- Alternative meaning search: if any literal meanings are matched this search begins. This search takes the synonyms of the literal meaning as saved in the words dictionary entry, and uses those to search words with the same literal meaning. 

The aim here is to find any words that are already translated into Arcana, find any words with the same meaning translated in Arcana, find any word that could be interpreated as the same, and finally suggest alternative words that could be used or used for a new search. 

Furthermore, slide bars have been added to the translator windows so more text can be sent for translation. And the translated text has been covereted into a box which slides and can be copied through the click of a button, text itself cannot be selected to avoid unforseen interaction errors. 

---

## Current Features

### Home Screen

The application opens with three main options:

---

### 1. Search Dictionary

Allows users to search the current active dictionary using multiple methods:

* **Partial English Search**
  Finds entries with similar meanings or related synonyms.

* **Exact English Search**
  Returns entries with exact meaning matches.

* **Partial Arcana Search**
  Finds entries containing matching letter patterns.

* **Exact Arcana Search**
  Returns exact matches for Arcana words.

**Results Display:**

* Word definition
* Synonyms
* Word type

---

### 2. Translator

Accepts input in either English or Arcana and attempts translation in three stages:

1. **Exact Match**
   Matches words directly by meaning or Arcana equivalent

2. **Synonym Matching**
   Searches for words with similar meanings

3. **Suggestion System**
   Recommends alternative words where no direct translation exists

---

### 3. Dictionary Editor

Provides full control over the active dictionary:

* Add, edit, or remove entries
* Save changes to the active dictionary

**Dictionary Types:**

* **Active Dictionary**
  The current working file used by all features

* **Backup Dictionaries**
  Up to 6 backups are maintained:

  * 1 default backup
  * 5 rotating backups that update as changes are made

* **Core Dictionary**
  The base dictionary maintained by the developer

  * Should not be edited
  * Used to restore the system if the active dictionary is lost
  * To reset: copy the core file and remove the `_core` suffix

---

## Project Goal

To create a flexible, evolving Arcana language system that:

* Supports both canonical and extended vocabulary
* Provides intelligent translation and substitution tools
* Enables users to expand the language where needed
* Maintains a stable core while allowing creative adaptation

---
