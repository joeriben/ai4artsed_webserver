#!/bin/bash

# Hole die neuesten Änderungen vom Remote-Repository
git fetch origin

# Zeige die Unterschiede zwischen deinem lokalen 'main' und dem Remote
echo -e "\nDifference between local and remote:"
git diff main origin/main

# Zeige das commit log im Graph-Format für bessere Übersicht
echo -e "\nCommit log graph:"
git log --oneline --graph main origin/main

# Warten auf Enter-Taste, um das Fenster offen zu halten
read -p "Drücke Enter, um zu schließen..."

