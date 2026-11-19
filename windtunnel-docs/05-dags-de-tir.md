# Les DAGs de tir de l'image

L'image `windtunnel-airflow:3.2.2` embarque les DAGs de tir du dossier [dags/](../dags/). Chaque
DAG reproduit la **forme** d'un type de tâche réel, et met à l'épreuve les réglages qui s'y
rapportent.

## Un DAG par type de tâche

| DAG | Type de tâche | Ce que fait une tâche |
| --- | --- | --- |
| [`load_test`](../dags/load_test.py) | Tâche courte ou longue | Elle occupe une place de worker pendant la durée demandée |
| [`load_test_job`](../dags/load_test_job.py) | Tâche qui pilote un job externe | Elle charge le CPU du worker au démarrage, puis garde sa place sans rien consommer |
| [`load_test_deferred`](../dags/load_test_deferred.py) | Capteur différé | Elle attend sur le triggerer, sans place de worker, puis reprend sur un worker au réveil |
| [`load_test_many_dags`](../dags/load_test_many_dags.py) | Grand nombre de DAGs | Un seul fichier génère des DAGs inactifs, que le dag-processor doit lire |

## Les paramètres de chaque DAG

Les paramètres se passent au déclenchement du run. Seul le nombre de DAGs générés se fixe au
déploiement : il est lu à l'analyse du fichier.

| DAG | Paramètre | Ce qu'il règle | Défaut |
| --- | --- | --- | --- |
| `load_test` | `tasks` | Nombre de tâches du run | 10 |
| | `seconds` | Durée d'une tâche | 60 |
| `load_test_job` | `tasks` | Nombre de tâches du run | 10 |
| | `startup_seconds` | Durée de la charge CPU au démarrage | 10 |
| | `seconds` | Durée du job, place gardée | 60 |
| `load_test_deferred` | `sensors` | Nombre de capteurs du run | 10 |
| | `seconds` | Durée de l'attente | 60 |
| `load_test_many_dags` | `LOAD_TEST_DAG_COUNT` (variable d'environnement) | Nombre de DAGs générés | 0 |

## Les réglages mis à l'épreuve

Les réglages sont décrits dans [les réglages qui comptent](03-reglages.md).

| DAG | Ce que le tir regarde | Réglages en jeu |
| --- | --- | --- |
| `load_test`, tâches courtes | Les plafonds de concurrence et la formation de la file | `[core] parallelism`, `[core] max_active_tasks_per_dag`, `[core] default_pool_task_slot_count`, `workers.celery.replicas` × `[celery] worker_concurrency` |
| `load_test`, tâches longues | L'attente derrière les tâches longues, et leur sort à l'arrêt du worker | `[scheduler] task_queued_timeout`, `workers.celery.terminationGracePeriodSeconds`, `[core] default_task_retries` |
| `load_test`, plusieurs runs | Le partage des places entre runs | `[core] max_active_runs_per_dag`, `[core] parallelism`, `[core] default_pool_task_slot_count` |
| `load_test_job` | Le signal de l'autoscaling : CPU au démarrage, place gardée ensuite | `workers.celery.hpa`, `workers.celery.keda`, `[celery] worker_concurrency` |
| `load_test_deferred` | La capacité du triggerer, puis la reprise des tâches au réveil | `[triggerer] capacity` × `triggerer.replicas`, puis les plafonds de concurrence |
| `load_test_many_dags` | La lecture des fichiers par le dag-processor | `dagProcessor.replicas` |

Un tir de résilience n'a pas de DAG à lui : il arrête un composant pendant qu'un de ces DAGs
tourne.

## Trois limites à connaître

- **Une tâche de préparation ouvre chaque run.** Elle calcule la liste des tâches à lancer, et
  occupe elle-même une place pendant un court instant.
- **Un run lance 1024 tâches au plus.** C'est la valeur par défaut de `[core] max_map_length`,
  lue dans l'image.
- **Les capteurs d'un run se réveillent ensemble.** Ils partagent la même heure de réveil : la
  reprise arrive d'un coup sur les workers.
