# Tester une configuration par un tir de charge

Une configuration d'Airflow annonce, sans le dire, des **plafonds** (combien de tâches tournent en
même temps) et des **délais** (combien de temps une tâche peut attendre). Un tir de charge vérifie
ces annonces : il soumet la configuration à une charge connue, puis compare ce qui était prévu à
ce qui se passe.

```
configuration ──► prévu ──► tir ──► relevés ──► prévu vs mesuré
```

## 1. Lire ce que la configuration annonce

| Question | Réglages en jeu |
| --- | --- |
| Combien de tâches tournent en même temps ? | `[core] parallelism` × schedulers, `[core] max_active_tasks_per_dag`, places du pool, workers × `[celery] worker_concurrency` |
| Combien de temps une tâche peut-elle attendre en file ? | `[scheduler] task_queued_timeout` |
| Au bout de combien de temps une tâche orpheline est-elle déclarée en échec ? | `[scheduler] task_instance_heartbeat_timeout` |
| Une tâche survit-elle à l'arrêt de son worker ? | Le délai de grâce du worker, face au temps qui reste à la tâche |
| Combien de capteurs différés tiennent en attente ? | `[triggerer] capacity` × triggerers |

## 2. Chiffrer le prévu

**Le plafond réel est le plus petit des plafonds.** Le prévu s'écrit avant le tir, à partir de la
configuration seule.

Exemple avec une configuration fictive, un peu au-dessus des valeurs par défaut d'Airflow, et un
seul worker :

| Plafond | Réglage | Valeur |
| --- | --- | --- |
| Par scheduler | `[core] parallelism` | 40 |
| Par run d'un DAG | `[core] max_active_tasks_per_dag` | 20 |
| Par pool | `[core] default_pool_task_slot_count` | 160 |
| Places des workers | 1 worker × `[celery] worker_concurrency` | 20 |

Prévu : un run fait tourner **20 tâches** au plus.

## 3. Encadrer chaque plafond

Un plafond se vérifie par trois tirs : en dessous, pile, au-dessus.

| Tir | Prévu |
| --- | --- |
| 10 tâches | Toutes démarrent tout de suite |
| 20 tâches | Toutes démarrent, il ne reste aucune place |
| 30 tâches | 20 tournent, 10 attendent leur tour |

Dans cet exemple, deux plafonds valent 20 : le tir ne dit pas lequel retient les 10 tâches. Pour
les distinguer, on change **un seul réglage**, puis on tire de nouveau.

## 4. Relever

Le relevé suit l'état des tâches dans le temps : `scheduled`, `queued`, `running`, `success`,
`failed`. Il est **horodaté** et se fait **en lecture seule** : un relevé ne modifie pas ce qu'il
mesure.

## 5. Comparer le prévu et le mesuré

Chaque écart est relié au réglage qui l'explique. Une cause qui n'a pas été vérifiée s'écrit
« non vérifiée ».

La suite : [adapter le tir aux tâches réelles](02-adapter-le-tir.md), puis
[les réglages qui comptent](03-reglages.md).
