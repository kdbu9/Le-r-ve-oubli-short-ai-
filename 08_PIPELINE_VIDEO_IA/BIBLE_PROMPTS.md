# Bible des prompts — Le rêve oublié (pipeline vidéo IA)

> **Statut : v1, à valider par le directeur artistique.** Les prompts sont en anglais, la langue que les modèles comprennent le mieux. Les blocs ci-dessous se **copient tels quels** pour que chaque génération décrive les personnages exactement de la même façon. C'est la base de la cohérence d'un plan à l'autre.

## 1. Règles

1. **Toujours joindre les images de référence** du personnage (`REFERENCES_IA/`) en plus du texte. Le texte seul ne suffit pas à garder un visage stable.
2. **Ne jamais nommer un studio, un film ou un personnage existant** dans les prompts. On décrit le style par ses caractéristiques (bloc STYLE). C'est la règle du dossier, et beaucoup d'outils refusent ou dégradent ce type de demande.
3. **Aucun texte généré à l'image.** Les cartons, le texte final et les inscriptions se font au montage. Les IA déforment les lettres. Ajouter « no text, no letters, no logos » quand un vêtement ou une enseigne est visible.
4. **Origine** : décrire l'apparence (« Black, of African descent »), jamais une nationalité précise. Celle-ci n'est pas définie.
5. **La mère** est toujours décrite comme aimante, même quand elle est ferme. Proscrire « angry », « cruel » ou « shouting ».
6. **Fin verrouillée** : aucun prompt ne montre l'agent parler aux enfants, les encourager ou rejouer avec eux.
7. Une génération = un plan court (4 à 10 s). Les plans longs se construisent par montage, pas par une seule génération.

## 2. Bloc STYLE (à coller dans tous les prompts)

```
Stylized 3D animated feature film, high-end CG animation render. Appealing character design with soft rounded shapes, large expressive eyes, nuanced facial expressions, warm subsurface-scattering skin with natural tones, detailed textured coily hair, believable fabric. Cinematic composition, soft volumetric lighting, gentle depth of field, rich but natural color palette. No text, no letters, no logos, no watermark.
```

### Variantes de lumière (bible graphique, contraste temporel)

| Code | Usage | Bloc à ajouter |
|---|---|---|
| `LUM_PRESENT` | Séq. 1 et 5 (présent) | `Natural daylight, slightly muted palette, soft overcast-to-sunny sky, everyday realism, subtle navy and grey tones.` |
| `LUM_SOUVENIR` | Séq. 2 (match) | `Golden hour memory, warm glowing amber light, vivid saturated colors, light haze and lens bloom, nostalgic and joyful.` |
| `LUM_MAISON` | Séq. 3 (famille) | `Warm interior lamp light at dusk, cozy amber and cream tones, intimate framing, soft shadows.` |
| `LUM_RENONCEMENT` | Séq. 4 | `Quiet desaturated light, calm static framing, cooler tones, sense of time passing.` |

## 3. Personnages

### `PERSO_AMADOU_ADULTE` — références : `REF_amadouAdulte_visage.png`, `REF_amadouAdulte_turnaround.png`
```
Amadou, a 42-year-old Black man of African descent, warm medium-dark brown skin, round friendly face, short dense black coily hair, short full black beard with a neat mustache, kind brown eyes that look slightly tired, a discreet gentle smile, medium build, a little heavier than in his youth. Wearing a navy blue long-sleeve work top, a fluorescent yellow high-visibility safety vest with silver reflective stripes and no writing, dark navy cargo work trousers, black work boots.
```

### `PERSO_AMADOU_ADO` — références : `REF_amadouAdo_visage.png`, `REF_amadouAdo_turnaround.png`, `REF_amadou_duo_portrait.png`
```
Young Amadou, a 16-year-old Black teenage boy of African descent, the same face as the adult Amadou but younger: warm medium-dark brown skin, short dense black coily hair, bright lively brown eyes, big spontaneous smile, slim athletic build. Wearing a burgundy football jersey with cream trim, burgundy shorts, long white socks and black football boots.
```
> À confirmer (question n° 11) : le numéro 10 sur le maillot. Il n'est pas inclus pour l'instant.

### `PERSO_MERE` — références : `REF_mere_portrait.png`, `REF_mere_turnaround.png`, `REF_mere_expressions.png`
```
Amadou's mother, a Black woman of African descent around 42 years old, warm dark brown skin, round kind face, expressive eyes, full figure. Wearing a long colorful wax-print dress with a burgundy and golden-ochre fan pattern, a matching head wrap, small gold hoop earrings. Loving, protective and determined; even when firm, her face shows care and worry, never anger.
```

### Personnages secondaires (à concevoir : faire valider une image de référence avant de les animer)

`PERSO_COLLEGUE` (proposition) :
```
A municipal co-worker in his fifties, friendly weathered face, short grey hair, same navy work top and yellow high-visibility vest with no writing as Amadou.
```
`PERSO_ENTRAINEUR` (proposition) :
```
A neighborhood youth football coach in his forties, tracksuit in navy and cream, whistle around the neck, warm proud expression.
```
`PERSO_ENFANTS_PRESENT` :
```
A diverse group of 6 to 8 neighborhood kids aged 9 to 12, mixed backgrounds, casual colorful clothes and mismatched football jerseys with no logos, playing joyfully.
```
`PERSO_EQUIPES_SOUVENIR` :
```
Teenage players aged 15 to 17, one team in burgundy jerseys with cream trim, the other team in light blue jerseys, no logos, no numbers.
```

## 4. Décors

`DECOR_QUARTIER` :
```
A contemporary working-class neighborhood in a French city: 6-to-10-storey residential apartment buildings in cream, ochre and terracotta tones, balconies, trees along wide sidewalks, a small bakery and a corner grocery with plain awnings, benches, street lamps, neighbors of all ages passing by. Lived-in and warm, not run-down, not exotic.
```
`DECOR_TERRAIN` :
```
A neighborhood football pitch with green artificial turf and white lines, two small goals with nets, a tall green metal fence, apartment buildings and trees around it, a few parents watching from the low fence and benches on the side.
```
`DECOR_SALON` (lieu retenu pour la scène mère-fils, décision du 17/11/2026) :
```
A warm family living room: a worn fabric sofa with patterned cushions, a wooden coffee table and a small dining table where school notebooks lie open, a floor lamp, family photos on the wall, green plants on the windowsill, lived-in and modest, neither luxurious nor poor.
```
`DECOR_CHAMBRE` :
```
A teenage boy's small bedroom: a single bed with a navy blanket, a desk with school books and notebooks, a desk lamp, a football in the corner, a modest trophy and a football poster with no text on the wall.
```

## 5. Structure d'un prompt

**Image clé (première image du plan)**
```
[STYLE] [LUMIÈRE] [DÉCOR] [PERSONNAGE(S)] + action figée + cadrage (wide shot / medium shot / close-up, angle, focale).
```

**Vidéo (image vers vidéo)**
```
Uniquement le mouvement : ce qui bouge, comment la caméra bouge, l'émotion. Ne pas redécrire l'image.
Ex. : "Slow push-in on his face as his eyes drift away, a faint nostalgic smile appears. Kids' voices in the background."
```
