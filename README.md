# Arcana Dictionary – Version 0.1

## Overview

This project uses the existing Thuum canon as a structural foundation for an Arcana dictionary, search system, and translation tool.

It was developed in response to the closure of thuum.org to non-canon words. While that decision is understandable, it creates an opportunity to build a more flexible system—one that supports Arcana users in expanding and adapting the language.

The goal of this project is not only to provide search and translation tools, but also to bridge gaps in the Arcana dictionary where no direct words currently exist. Where necessary, the system will suggest alternatives based on similarity, synonym, or contextual meaning.

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
