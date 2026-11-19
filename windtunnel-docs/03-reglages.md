# Les réglages qui comptent

Un tir relie chaque constat à un réglage. Ces réglages sont de deux sortes : la **configuration
d'Airflow**, et l'**infrastructure** qui le porte.

## La configuration d'Airflow

| Réglage | Ce qu'il fixe | Défaut |
| --- | --- | --- |
| `[core] parallelism` | Tâches en cours, par scheduler | 32 |
| `[core] max_active_tasks_per_dag` | Tâches en cours, par run d'un DAG | 16 |
| `[core] max_active_runs_per_dag` | Runs en cours, par DAG | 16 |
| `[core] default_pool_task_slot_count` | Places du pool par défaut | 128 |
| `[celery] worker_concurrency` | Places par worker | 16 |
| `[scheduler] task_queued_timeout` | Temps passé en file avant relance ou échec | 600 s |
| `[scheduler] task_instance_heartbeat_timeout` | Temps sans battement avant qu'une tâche soit déclarée morte | 300 s |
| `[triggerer] capacity` | Capteurs différés par triggerer | 1000 |
| `[core] default_task_retries` | Relances d'une tâche en échec | 0 |
| `[dag_processor] health_check_threshold` | Temps sans battement avant qu'un dag-processor soit jugé en panne | 30 s |

Les défauts sont ceux d'Airflow 3.2.2, lus dans l'image `apache/airflow:3.2.2`.

## L'infrastructure

Les noms sont ceux des values du chart Helm officiel d'Airflow, version 1.22.0.

| Valeur du chart | Ce qu'elle fixe |
| --- | --- |
| `workers.celery.replicas` | Le nombre de workers |
| `workers.celery.hpa` | L'autoscaling des workers sur leur CPU et leur mémoire |
| `workers.celery.keda` | L'autoscaling des workers sur la charge de tâches |
| `workers.celery.terminationGracePeriodSeconds` | Le temps laissé à un worker arrêté pour finir ses tâches |
| `scheduler.replicas`, `apiServer.replicas`, `triggerer.replicas`, `dagProcessor.replicas` | Le nombre d'instances de chaque composant |

S'y ajoute la **capacité du cluster** : le nombre de nœuds et leurs ressources bornent le nombre
de workers qui peuvent réellement démarrer.

## Quatre pistes à vérifier par le tir

**1. Aligner les plafonds.** Le plus petit plafond gouverne. Un plafond réglé au-dessus des places
réelles des workers n'ajoute pas de capacité : il laisse entrer en file des tâches qui attendront.

**2. Choisir le signal de l'autoscaling.** Une tâche qui attend une réponse occupe une place sans
consommer de CPU. Un autoscaling sur le CPU peut alors ne pas voir une file qui s'allonge. Et le
maximum demandé n'est pas le maximum obtenu : au-delà de la capacité du cluster, les workers
restent en attente.

**3. Protéger les tâches longues.** Deux délais les menacent : le délai en file, quand elles
attendent derrière d'autres tâches longues, et le délai de grâce, quand leur worker s'arrête. Les
relances permettent à une tâche perdue de repartir sur un autre worker.

**4. Doubler les composants.** Avec deux instances d'un composant, l'arrêt de l'une doit rester
sans effet sur les tâches en cours.
