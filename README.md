# Prismalia

Un monde simple. Des règles élémentaires. Des possibilités infinies.

## Prototype jouable

Le dépôt contient un prototype minimal construit avec Python et Pygame.
Il met en place :

- Un rendu isométrique avec une carte procédurale plus naturelle.
- Un rendu isométrique avec une carte générée aléatoirement.
- Un joueur et un animal compagnon contrôlés par des animations.
- Un inventaire basique avec collecte de ressources.
- Un système d’assets configurable acceptant sprites PNG et spritesheets.

## Lancer le jeu

```bash
python -m venv .venv
source .venv/bin/activate  # Sous Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

Le jeu se ferme avec la touche `Échap` ou en fermant la fenêtre. Les contrôles
par défaut sont :

| Action            | Touche |
|-------------------|--------|
| Se déplacer       | ZQSD / Flèches |
| Interagir         | E |
| Ouvrir inventaire | I |
| Nourrir animal    | F |
| Interface logique | L |
| Interface logique | Q |

## Structure du code

```
prismalia/
├── assets.py        # Chargement sprites + placeholders
├── constants.py     # Constantes globales
├── entities.py      # Joueur, animal, base Entity
├── game_app.py      # Boucle de jeu
├── input.py         # Gestion des entrées clavier
├── inventory.py     # Inventaire et ressources
├── isoutils.py      # Conversion cartésien -> isométrique
├── tilemap.py       # Carte et génération procédurale
└── world.py         # Orchestration du monde + HUD
```

## Assets graphiques

Les images doivent être placées dans `assets/` en suivant le schéma logique :
`<categorie>/<nom>.png`. Les catégories actuellement utilisées sont `tiles`,
`player`, `animal` et pourront être étendues (`objects`, `ui`, etc.).

Les spritesheets doivent contenir les frames en ligne unique de largeur fixée.
La taille cible pour un tile isométrique est de 64x32 px (ratio 2:1). Les
animations du joueur et de l’animal utilisent la taille définie dans
`prismalia/constants.py`.

## Étapes suivantes

1. Intégration des sprites définitifs.
2. Ajout de la récolte contextuelle (arbres, rochers, etc.).
3. Construction et pose de blocs via l’inventaire.
4. Interface de programmation visuelle pour piloter le compagnon.
5. Progression (cycle jour/nuit, ressources rares, énergie).

Toute contribution est la bienvenue pour pousser ce bac à sable vers un système
Turing-complet !
