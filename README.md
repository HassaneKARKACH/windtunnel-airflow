# windtunnel-airflow

> *Partir d'une configuration d'Airflow, et montrer comment la tester par un tir de charge.*

**windtunnel-airflow** est un projet de démo qui illustre une démarche : tester une configuration
d'Airflow dans des conditions de production, sur un cluster Kubernetes ou des VM.

## Pourquoi

Une configuration d'Airflow se lit réglage par réglage, mais se comporte comme un tout : les
limites de concurrence, la capacité des workers et les délais en file décident **ensemble** de ce
qui se passe sous charge. Ce comportement ne se lit pas dans un fichier : il se mesure.

## La démarche

```
configuration ──► prévu ──► tir ──► relevés ──► prévu vs mesuré
```

1. Tirer de la configuration les plafonds et les délais **prévus**.
2. La soumettre à une charge connue, qui encadre chaque plafond : en dessous, pile, au-dessus.
3. **Relever** ce qui se passe, en lecture seule.
4. Comparer le prévu au mesuré, et relier chaque écart au réglage qui l'explique.

## Ce que doit expliquer la documentation

| Page | Question |
| --- | --- |
| [Le tir de charge](windtunnel-docs/01-tir-de-charge.md) | Comment tester une configuration d'Airflow par un tir de charge |
| [Adapter le tir](windtunnel-docs/02-adapter-le-tir.md) | Comment régler le tir selon les types de tâches et le contexte d'usage |
| [Les réglages](windtunnel-docs/03-reglages.md) | Quels réglages d'infrastructure et de configuration changer pour utiliser Airflow plus efficacement |
| [kind](windtunnel-docs/04-kind.md) | Comment le projet simule un cluster Kubernetes sur un poste |
| [Les DAGs de tir](windtunnel-docs/05-dags-de-tir.md) | Quel DAG de l'image reproduit quel type de tâche, et quels réglages il met à l'épreuve |

## Un cluster simulé

La démarche s'applique à un Airflow réel. Pour la montrer de bout en bout sans vrai cluster, le
projet déploie Airflow sur **kind**, un cluster Kubernetes local, avec le chart Helm officiel.

| Brique | Choix |
| --- | --- |
| Cluster | kind, sur Docker Engine |
| Déploiement | Chart Helm officiel d'Airflow 1.22.0 |
| Airflow | 3.2.2, CeleryExecutor |

Les commandes se lancent depuis Ubuntu (WSL), à la racine du dépôt :

```console
$ make cluster   # crée le cluster kind et pose le label de chaque worker
$ make images    # construit l'image d'Airflow avec les DAGs de tir, et charge les images dans les nœuds
$ make chart     # installe Airflow
$ make down      # supprime le cluster
```
