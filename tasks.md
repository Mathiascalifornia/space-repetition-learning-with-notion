Fonctionnalités : 

- Il y aura un petit menu, qui laissera à l'utilisateur le choix du/des sujets à étudier/exclure.  de type ; 
1) tout les sujets 
2) sujet1 (dernière révision : n sessions) 
3) sujet2 (dernière révision : n sessions) 
4) supprimer un sujet pour cette session
5) Reinitialiser les sujets supprimé
6) Remélanger la structure de donnée

- Ensuite, une fois qu'un "filtre" a été choisi, le système retournera une sous page (seulement le nom de la sous page) , et si l'utilisateur valide (Y/n) , le lien de cette sous page sera renvoyé à l'utilisateur afin qu'il aille lire la sous page, et la sous page en question sera placé en tout début de la queue. 
- Il faut que chaque page principale ait sa propre structure (pour pouvoir appliquer le système à un sujet particulier). Idéalement, quelque chose de type dictionnaire pour avoir UNE seule structure permettant de gérer tout le système
- Il faut pouvoir exclure un sujet de la liste (mais pas de manière persistante), par exemple au cas où je veuille me débarrasser de tout ce qui n'est pas informatique pour une session donnée, ou alors je ne veuille travailler que des sujets finances et dev perso. Il faut aussi que les sujets révisés soit quand même placé au début de la queue dans la structure principale
- Il faut une structure principale où tout est mélangé
- Il faut que l'utilisateur puisse refuser de voir une page. Dans ce cas, la page est renvoyer quelque part entre 5 et 10 places en arrière
- Il faut que la structure soit persistante (qu'on puisse la sauvegarder facilement) 
- Il faut que la structure soit scalable (que le système puisse facilement s'adapter si des nouvelles pages sont détectés, sans modifier la structure en place). Les nouvelles pages seront placées au début de la structure (je pars du principe que si la page vient d'être crée c'est que le concept est frais dans ma tête) 