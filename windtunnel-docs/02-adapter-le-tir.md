# Adapter le tir aux tâches réelles

Un tir ne vaut que s'il ressemble à l'usage. Une tâche de tir ne calcule rien : elle **occupe une
place**. Ce qui compte est sa forme : combien de tâches, pendant combien de temps, et sur quel
composant elles attendent.

## Les paramètres d'un tir

| Paramètre | Ce qu'il met à l'épreuve |
| --- | --- |
| Nombre de tâches par run | Le plafond par run et les places des workers |
| Nombre de runs simultanés | Le plafond par scheduler, le pool, l'ordre de service de la file |
| Durée d'une tâche | Le délai en file et le délai de grâce des workers |
| Type de tâche | Le composant sollicité : worker ou triggerer |
| Nombre de DAGs | Le dag-processor |
| Incident injecté | La résilience : arrêt d'un worker, d'un scheduler, d'un api-server |

## Les types de tâches

| Type de tâche | Usage réel | Ce que le tir regarde |
| --- | --- | --- |
| Tâche courte | Appel d'API, requête SQL, transfert de fichier | Les plafonds de concurrence et la formation de la file |
| Tâche longue | Traitement lourd, export | Les tâches qui attendent derrière elle, face au délai en file ; son sort à l'arrêt du worker |
| Tâche qui pilote un job externe | Soumission d'un job à un moteur de calcul | La place gardée tant que le job tourne ; la charge du worker au démarrage du client |
| Capteur différé | Attente d'un fichier, d'un événement, d'une heure | La capacité du triggerer ; le rythme de reprise des tâches au réveil |
| Grand nombre de DAGs | Plateforme partagée, DAGs générés | Le temps de lecture des fichiers par le dag-processor |

## Régler le tir selon le contexte

**Les rapports comptent plus que les valeurs.** Un tir se règle par rapport aux plafonds et aux
délais de la configuration testée. Une maquette à échelle réduite garde ces rapports et réduit les
valeurs absolues.

| Rapport | Prévu en dessous de 1 | Prévu au-dessus de 1 |
| --- | --- | --- |
| Tâches demandées / places | Tout démarre | Une file se forme |
| Durée d'une tâche / délai en file | La file se vide avant le délai | Des tâches dépassent le délai en file |
| Temps restant à la tâche / délai de grâce | La tâche finit avant l'arrêt du worker | La tâche est tuée avec le worker |

Le contexte donne les valeurs : la durée des tâches réelles, le nombre de runs qui se chevauchent
aux heures de pointe, la part de tâches en attente d'un événement.

## Injecter un incident

Un tir de résilience ajoute un incident à une charge en cours : l'arrêt d'un worker, d'un
scheduler ou d'un api-server. Le prévu s'écrit de la même façon : quelles tâches finissent,
lesquelles sont perdues, et au bout de combien de temps Airflow le constate.
