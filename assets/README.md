# Assets directory

Place generated sprites and sprite sheets here following the logical naming
convention used by the asset manager. For example:

```
assets/
├── player/
│   ├── idle.png        # Sprite sheet with idle animation frames in a row
│   └── walk.png        # Sprite sheet with walking animation frames in a row
├── animal/
│   ├── idle.png
│   └── walk.png
└── tiles/
    ├── grass.png
    ├── dirt.png
    ├── rock.png
    ├── sand.png
    └── water.png
```

Static sprites should be exported as PNG with transparency preserved. Animation
sheets are read row by row and split into frames of equal size.
