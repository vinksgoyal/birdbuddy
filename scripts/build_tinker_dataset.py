"""Build a small, fully offline Tinker chat dataset about North American birds."""

import json
from pathlib import Path


SPECIES = [
    ("American Robin", "Turdus migratorius", "a familiar thrush with an orange-red breast", "lawns, parks, woodland edges, and gardens", "a clear, musical series of rising and falling phrases"),
    ("Northern Cardinal", "Cardinalis cardinalis", "a crested songbird whose male is brilliant red and whose female is warm brown", "thickets, forest edges, suburbs, and backyard feeders", "a repeated, whistled cheer-cheer or birdy-birdy phrase"),
    ("Blue Jay", "Cyanocitta cristata", "a large blue-and-white corvid with a prominent crest", "oak woods, forest edges, parks, and neighborhoods", "loud jays, whistles, and harsh rising calls"),
    ("Mourning Dove", "Zenaida macroura", "a slim, long-tailed dove with soft gray-brown plumage", "open country, farms, suburbs, and woodland edges", "a low, mournful coo that is often repeated"),
    ("American Crow", "Corvus brachyrhynchos", "a large, all-black and highly adaptable corvid", "farmland, towns, parks, and open woodland", "a familiar, emphatic caw with varied rhythm"),
    ("Black-capped Chickadee", "Poecile atricapillus", "a small chickadee with a black cap, bib, and white cheeks", "mixed forests, streamside woods, and backyards", "a clear fee-bee song and nasal chick-a-dee calls"),
    ("Tufted Titmouse", "Baeolophus bicolor", "a gray songbird with a pointed crest and rusty flanks", "deciduous woods, wooded suburbs, and mature parks", "a repeated peter-peter-peter whistle"),
    ("White-breasted Nuthatch", "Sitta carolinensis", "a compact nuthatch that commonly moves headfirst down tree trunks", "mature forests, orchards, and large trees near homes", "a nasal yank or series of short, nasal notes"),
    ("Carolina Wren", "Thryothorus ludovicianus", "a compact cinnamon-brown wren with a bold white eyebrow", "brush piles, dense shrubs, wood edges, and porches", "a loud tea-kettle-teakettle song"),
    ("House Wren", "Troglodytes aedon", "a small, plain brown wren with a cocked tail", "backyards, brushy edges, gardens, and nest boxes", "a bubbling cascade of rapid trills and rattles"),
    ("Eastern Bluebird", "Sialia sialis", "a thrush with a blue back and rusty-orange breast", "open fields, orchards, pasture edges, and nest-box habitats", "a soft, warbling series of musical phrases"),
    ("Wood Thrush", "Hylocichla mustelina", "a spotted woodland thrush with a rusty-brown back", "shady, mature deciduous forest with leaf litter", "an ethereal song with clear flute-like notes and overlapping phrases"),
    ("Gray Catbird", "Dumetella carolinensis", "a slate-gray songbird with a black cap and rusty undertail", "dense shrubs, thickets, woodland edges, and gardens", "a varied jumble of whistles, squeaks, and imitations"),
    ("Northern Mockingbird", "Mimus polyglottos", "a gray-and-white songbird famous for copying other birds", "open suburbs, towns, scrub, and field edges", "long streams of repeated phrases and imitations, often day or night"),
    ("Brown Thrasher", "Toxostoma rufum", "a long-tailed, rusty-backed bird with a strongly streaked breast", "dense brush, hedgerows, and woodland margins", "a rich series of phrases usually delivered twice"),
    ("Common Yellowthroat", "Geothlypis trichas", "a small olive warbler whose male wears a black facial mask", "marshes, wet thickets, and dense field edges", "a brisk wichity-wichity-wichity song"),
    ("Yellow Warbler", "Setophaga petechia", "a bright yellow warbler often marked with rusty breast streaks", "willows, stream edges, wet thickets, and young woodland", "a sweet, rising sweet-sweet-sweet song"),
    ("American Redstart", "Setophaga ruticilla", "an active black-and-orange warbler that fans its tail", "deciduous woods, forest edges, and shady second growth", "a bright, slightly emphatic series of see-see-see notes"),
    ("Black-and-white Warbler", "Mniotilta varia", "a boldly striped warbler that creeps along tree trunks", "mature deciduous and mixed forests", "a high, accelerating weesy-weesy-weesy song"),
    ("Ovenbird", "Seiurus aurocapilla", "a ground-walking woodland warbler with an orange crown stripe", "large mature forests with deep leaf litter", "a loud, ringing teacher-teacher-TEACHER song"),
    ("Scarlet Tanager", "Piranga olivacea", "a red male and olive-yellow female tanager of leafy forests", "large deciduous forest, especially high in the canopy", "a hoarse, robin-like series of burry phrases"),
    ("Rose-breasted Grosbeak", "Pheucticus ludovicianus", "a thick-billed songbird whose male has a red breast triangle", "deciduous woods, forest edges, and backyard feeders", "a rich, rolling whistle that resembles a softer robin song"),
    ("Indigo Bunting", "Passerina cyanea", "a small finch-like songbird with a deep blue male in breeding season", "brushy fields, roadsides, and woodland clearings", "a series of paired, cheerful notes"),
    ("Song Sparrow", "Melospiza melodia", "a streaked sparrow with a variable brown pattern", "brushy edges, wetlands, farms, and suburban gardens", "a varied opening note followed by several musical phrases"),
    ("White-throated Sparrow", "Zonotrichia albicollis", "a brown sparrow with a bright white throat and striped crown", "wood edges, shrubby understory, and winter gardens", "a clear whistle often remembered as old-Sam-Peabody-Peabody"),
    ("Chipping Sparrow", "Spizella passerina", "a small sparrow with a rusty crown and crisp facial line", "open pine woods, fields, parks, and lawns", "a dry, accelerating mechanical trill"),
    ("Dark-eyed Junco", "Junco hyemalis", "a variable-colored sparrow with a neat, pale belly", "coniferous and mixed woods, brush, and winter feeders", "a simple, musical trill"),
    ("House Finch", "Haemorhous mexicanus", "a common finch whose male has red on the head and breast", "towns, suburbs, desert washes, and open woodland", "a cheerful, warbling song with a buzzy ending"),
    ("American Goldfinch", "Spinus tristis", "a small finch with bright yellow breeding plumage and black wings", "weedy fields, thistle patches, open woodland, and feeders", "a long, twittering sequence with fluid notes"),
    ("Purple Finch", "Haemorhous purpureus", "a chunky finch with raspberry-red coloring on the male's head and breast", "coniferous and mixed forests and winter feeding stations", "a rich, musical warble that often ends with a distinctive zree"),
    ("Pine Siskin", "Spinus pinus", "a streaked, slender finch with a narrow pointed bill", "conifer forests, weedy edges, and cone-bearing trees", "a rapid, rising jumble of buzzy notes"),
    ("Red-winged Blackbird", "Agelaius phoeniceus", "a blackbird whose male shows a red-and-yellow shoulder patch", "freshwater marshes, wet meadows, and agricultural fields", "a nasal, gurgling konk-a-ree"),
    ("Common Grackle", "Quiscalus quiscula", "a long-tailed blackbird with glossy, often iridescent feathers", "marshes, farms, towns, and open woodland", "a harsh, croaking song with squeaks and whistles"),
    ("Baltimore Oriole", "Icterus galbula", "an orange-and-black songbird that forages high in leafy trees", "open deciduous woodland, parks, and mature neighborhoods", "a clear, whistled series of flute-like phrases"),
    ("Brown-headed Cowbird", "Molothrus ater", "a stocky blackbird whose male has a brown head", "open fields, pastures, woodland edges, and feedlots", "a short, liquid gurgle that drops in pitch"),
    ("European Starling", "Sturnus vulgaris", "a dark, speckled introduced bird with a pointed bill", "towns, farms, lawns, and open country", "a varied collection of whistles, rattles, and copied sounds"),
    ("Cedar Waxwing", "Bombycilla cedrorum", "a sleek, crested bird with a silky brown body and yellow-tipped tail", "berry-rich woodland edges, orchards, parks, and stream corridors", "high, thin trills given by flocks in contact"),
    ("House Sparrow", "Passer domesticus", "a compact introduced sparrow with a conical bill", "buildings, city streets, farms, and residential areas", "a simple series of cheeps and chirps"),
    ("American Kestrel", "Falco sparverius", "a small falcon with a rusty back and bold facial markings", "open fields, pasture, grassland, and roadside habitats", "a rapid, high-pitched klee-klee-klee call"),
    ("Red-tailed Hawk", "Buteo jamaicensis", "a broad-winged hawk with a characteristic rusty-red tail in adults", "open country, forest edges, ridges, and roadside perches", "a descending, raspy scream"),
    ("Cooper's Hawk", "Accipiter cooperii", "a long-tailed woodland hawk with rounded wings", "mature woods, suburbs, and wooded parks", "a series of sharp, rapid kek-kek-kek notes"),
    ("Bald Eagle", "Haliaeetus leucocephalus", "a large fish-eating eagle with a white head and tail in adults", "lakes, rivers, coasts, and large trees near water", "a surprisingly high, whistled chitter"),
    ("Great Horned Owl", "Bubo virginianus", "a large owl with prominent ear tufts and a deep body", "woodlands, farms, suburbs, and open country", "a deep, rhythmic hoot often rendered who-who-who"),
    ("Barred Owl", "Strix varia", "a large brown woodland owl with dark horizontal barring", "mature forests, swamps, and wooded ravines", "a distinctive eight-note who-cooks-for-you call"),
    ("Eastern Screech-Owl", "Megascops asio", "a small, stocky owl with ear tufts and variable gray or red plumage", "woodlots, orchards, suburbs, and parkland", "a descending whinny or steady, tremolo-like trill"),
    ("Killdeer", "Charadrius vociferus", "a brown-and-white shorebird with two dark breast bands", "mudflats, gravel, fields, lawns, and shorelines", "a loud, repeated kill-deer call"),
    ("American Woodcock", "Scolopax minor", "a chunky, long-billed woodland shorebird with cryptic brown plumage", "moist young forest, old fields, and brushy edges", "a nasal peent followed by twittering flight sounds"),
    ("Great Blue Heron", "Ardea herodias", "a tall, blue-gray wading bird with a long bill and legs", "ponds, rivers, marshes, and coastal shallows", "a harsh, deep croak when disturbed"),
    ("Canada Goose", "Branta canadensis", "a large goose with a black head and white cheek patch", "lakes, rivers, lawns, fields, and city ponds", "loud, honking calls in flight or on the ground"),
    ("Mallard", "Anas platyrhynchos", "a familiar dabbling duck whose male has a green head", "ponds, marshes, slow rivers, and urban waterways", "the female's descending quack and the male's quieter raspy calls"),
    ("Belted Kingfisher", "Megaceryle alcyon", "a large, crested waterbird that hunts fish from perches", "rivers, lakes, ponds, and coastal water", "a loud, dry, rattling call along the water"),
    ("Downy Woodpecker", "Dryobates pubescens", "a tiny black-and-white woodpecker with a short bill", "deciduous woods, orchards, parks, and feeders", "a sharp pik note and fast drumming"),
    ("Hairy Woodpecker", "Dryobates villosus", "a larger black-and-white woodpecker with a long bill", "mature forests, wooded parks, and large trees", "a strong peek call and measured drumming"),
    ("Northern Flicker", "Colaptes auratus", "a large brown woodpecker with a spotted breast and flashing wing color", "open woodland, forest edges, lawns, and dead trees", "a loud wick-wick-wick and a rolling rattle"),
    ("Pileated Woodpecker", "Dryocopus pileatus", "a crow-sized woodpecker with a vivid red crest", "mature forests with large dead trees", "a loud, irregular kuk-kuk-kuk series"),
    ("Eastern Phoebe", "Sayornis phoebe", "a plain flycatcher that often pumps its tail from a perch", "woodland edges, bridges, farms, and buildings near water", "a two-part raspy fee-bee"),
    ("Great Crested Flycatcher", "Myiarchus crinitus", "a large flycatcher with a peaked head and rusty wing panels", "woodland edges, open forest, and mature parks", "a loud whee-eep or prrrreet call"),
    ("Barn Swallow", "Hirundo rustica", "a graceful swallow with a deeply forked tail and rusty throat", "farms, wetlands, bridges, and open country", "a rapid twittering and cheerful chattering"),
    ("Common Nighthawk", "Chordeiles minor", "a mottled, long-winged bird that feeds on insects at dusk", "open fields, cities, shorelines, and upland habitats", "a nasal peent and a deep booming sound from display dives"),
    ("Chimney Swift", "Chaetura pelagica", "a slender, cigar-shaped bird that spends much of its life in flight", "towns and cities with chimneys, plus open airspace", "a continuous series of rapid, high chipping notes"),
]

QUESTIONS = (
    ("Give me a field note for {name}", "note"),
    ("Where can I find {name}?", "habitat"),
    ("How do I identify {name} by sound?", "sound"),
)
HOLDOUT_NAMES = {"American Kestrel", "Great Blue Heron", "Belted Kingfisher", "Barn Swallow", "Chimney Swift"}


def make_answer(name: str, scientific_name: str, detail: str, kind: str) -> str:
    if kind == "note":
        return f"{name} ({scientific_name}) is {detail}. Its shape, plumage, and behavior are useful clues when recording a field observation."
    if kind == "habitat":
        return f"Look for {name} in {detail}. Check the habitat near cover, food, or water, and listen before approaching."
    return f"Listen for {name}'s {detail}. Compare the rhythm, pitch, and repetition with nearby calls, since wind and other birds can alter what you hear."


def build_example(species: tuple[str, str, str, str, str], kind: str) -> dict:
    name, scientific_name, note, habitat, sound = species
    details = {"note": note, "habitat": habitat, "sound": sound}
    return {
        "messages": [
            {"role": "user", "content": next(q for q, q_kind in QUESTIONS if q_kind == kind).format(name=name)},
            {"role": "assistant", "content": make_answer(name, scientific_name, details[kind], kind)},
        ]
    }


def main() -> None:
    assert len(SPECIES) == 60
    assert len(HOLDOUT_NAMES) == 5
    assert all(len(species) == 5 for species in SPECIES)

    train = []
    validation = []
    for species in SPECIES:
        target = validation if species[0] in HOLDOUT_NAMES else train
        target.extend(build_example(species, kind) for _, kind in QUESTIONS)

    Path("data").mkdir(exist_ok=True)
    with Path("data/tinker_train.jsonl").open("w", encoding="utf-8") as file:
        for example in train:
            file.write(json.dumps(example, ensure_ascii=False) + "\n")
    with Path("data/tinker_val.jsonl").open("w", encoding="utf-8") as file:
        for example in validation:
            file.write(json.dumps(example, ensure_ascii=False) + "\n")
    print(f"Wrote {len(train)} training examples and {len(validation)} validation examples.")


if __name__ == "__main__":
    main()
