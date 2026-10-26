# Donkey Kong Country: Kong Swap

A ROM hack of **Donkey Kong Country** (SNES, USA v1.0) that adds **Kiddy Kong** (from DKC3), **Dixie Kong** (from DKC2), **Cranky Kong**, **Candy Kong** and **Funky Kong** as playable characters. On the world map, **R cycles DK → Kiddy → Cranky → Funky** and **L cycles Diddy → Dixie → Candy**. Cranky, Candy and Funky have to be unlocked first (see below).

![The four pairs on the world map](docs/images/independent_swap.png)
![Level stats on the world map](docs/images/map_stats.png)
![Gold faces for 100% levels (before / after)](docs/images/gold_icons.png)
![A missing partner shown as a ghost](docs/images/ghost_partner.png)
![Cranky and Candy on the world map](docs/images/cranky_candy_map.png)
![Funky surfing, jumping on his board, and on the world map](docs/images/funky.png)

## Features

- **Funky Kong** (new in 5.0) is playable once your file is **100% complete**: every banana and all four K-O-N-G letters in every level. Hold **Y** to ride his **surfboard**: he goes twice as fast as a running DK, knocks out the enemies he rides into, and a jump started on the board goes higher than Diddy's. His art is his DKC2 Funky's Flights II sprite with a drawn surfboard.
- **Unlocking** (new in 5.0): **Cranky** joins the R cycle once you've visited **all six Cranky's Cabins**, and **Candy** joins the L cycle once you've **saved at all six Candy's Save Points**. Visits and saves are recorded with your save file (a cabin visit is kept the next time you save). Until then those Kongs are skipped when you press R or L.
- **Collected bananas stay collected** (new in 4.3): every banana and banana bunch you pick up is remembered with your save file, so when you go back into a level the bananas you already have are gone and only the ones you missed are left.
- **Level stats on the world map**: the top-left corner shows how many of the level's bananas you've collected next to its total (bonus rooms included, a bunch counts as 10), and a **K** once you've collected all four K-O-N-G letters there. When a level is 100% complete (every banana and all four letters), the face of the Kong who beat it turns **gold** on the map. Everything is saved with your game at Candy's.
- **The banana counter keeps counting past 100** (new in 4.3): you still get an extra life every 100 bananas, but the counter goes on to 101, 102 and so on (up to 999) instead of starting over.
- **Pick each Kong independently any time on the world map**: **R** cycles the lead Kong (DK → Kiddy → Cranky → Funky) and **L** cycles the partner (Diddy → Dixie → Candy). Both Kongs on the map update right away. DK & Diddy stay exactly as in the original game.
- **Cranky Kong** (new in 3.0) uses DKC1's own Cranky art, including his unused walk cycle. He **swings his cane** instead of rolling.
- **Candy Kong** (new in 3.0) uses her DKC1 art plus newly made walking, running, jumping, swimming, climbing and carrying frames. Her attack is a **blown kiss**, holding Down plays her whole bend-over-and-blow-a-kiss animation, crawls on her front, and she swoons when hit.
- **Both Kongs always appear on the world map.** If one of them is missing (lost in a level, or Diddy still captured at the start), they follow along as a pale **ghost**, so you can always see which two Kongs you have picked.
- **Dixie's Helicopter Spin**: jump (or walk off a ledge), then hold **B** to twirl her ponytail and float down.
- **Kiddy's Ground Pound**: press **Down** in mid-air. He pauses, flips, and slams down butt-first.
  - Shatters hidden bonus-room walls (the ones Rambi or a barrel would break).
  - Pops buried items out of the ground (the spots DK's hand slap opens).
  - Hold Down after landing to stay seated.
- **Full sprite sets** from DKC2/DKC3 for walking, running, jumping, rolling, swimming, ropes, barrels, hurt and victory.
- **Riding animal buddies** (Rambi, Expresso, Winky, Enguarde) and **mine carts**.
- **World map and island sprites** for both Kongs, plus their **faces on beaten levels**.
- **Correct colours everywhere**, including dark, rainy, lightning and murky-water levels, Cranky's, Funky's, Candy's, and the extra-life balloon.

![Dixie's helicopter spin and barrel carrying](docs/images/dixie_spin_and_barrels.png)
![Kiddy's ground pound](docs/images/kiddy_ground_pound.png)
![Riding Rambi and mine carts](docs/images/riding.png)
![Cranky and Candy in levels](docs/images/cranky_candy_levels.png)
![World map sprites](docs/images/world_map.png)
![Level-complete faces](docs/images/level_faces.png)

## Playing it

1. Get a **clean, headerless** dump of *Donkey Kong Country (USA) v1.0* from a cartridge you own.
   SHA-256: `fa8cacf5bbfc39ee6bbaa557adf89133d60d42f6cf9e1db30d5a36a469f74d15`
2. Apply [`patches/dkc1_kong_swap_v5.0.bps`](patches/dkc1_kong_swap_v5.0.bps) (recommended, because it checks that you used the right ROM) or [`patches/dkc1_kong_swap_v5.0.ips`](patches/dkc1_kong_swap_v5.0.ips) (for patchers that only support IPS) with [Floating IPS](https://www.smwcentral.net/?p=section&a=details&id=11474) or [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/).
3. Play in any accurate SNES emulator (tested in snes9x and bsnes).

The patched ROM is 8 MB (ExHiROM) with 8 KB of save RAM (up from 2 KB) to hold the collected-banana records. Delete any old `.srm` from versions before 4.3 if your emulator complains about its size; your files keep working either way. Files saved with 4.3 or earlier have no cabin or save-point records yet, so Cranky and Candy start locked on them until you visit those places again. The v1.0 patches (which switch both Kongs together with L or R) are still in `patches/`. Older versions are on the Releases page.

**No ROMs are included in this repository, and please don't open issues or pull requests containing ROMs.**

## Building from source

The hack is built from your own copies of all three games. The Kiddy and Dixie graphics are read straight out of your DKC2 and DKC3 ROMs.

Requirements: Python 3.9+, `pip install -r requirements.txt`, and [asar](https://github.com/RPGHacker/asar) v1.9+ on your `PATH` (or set `ASAR=/path/to/asar`).

Put your clean, headerless USA ROMs in `roms/`:

| File | Game | SHA-256 |
|---|---|---|
| `roms/dkc1.sfc` | Donkey Kong Country (USA) v1.0 | `fa8cacf5…f74d15` |
| `roms/dkc2.sfc` | Donkey Kong Country 2 (USA) (En,Fr) | `35421a9a…8d8633` |
| `roms/dkc3.sfc` | Donkey Kong Country 3 (USA) (En,Fr) | `2277a2d8…94a32b` |

Then run:

```sh
python3 tools/build.py
```

This writes `build/dkc1_kong_swap.sfc`, `build/dkc1_kong_swap.bps` and `build/dkc1_kong_swap.ips`. The build is deterministic, so with the correct ROMs it reproduces the released patch byte for byte. You can also point to the ROMs with the `DKC1_ROM`, `DKC2_ROM` and `DKC3_ROM` environment variables.

### How it works

- `src/kong_swap.asm`: all new 65816 code (assembled with asar). It covers the per-Kong switches (three choices each), the alternate frame-table and palette lookups, the map hooks, the helicopter spin, the ground pound, held-barrel placement and the level-complete faces.
- `tools/build.py`: expands DKC1 to 8 MB ExHiROM. It builds alternate sprite-frame tables (one per new Kong) where DK/Diddy poses point at matching Kiddy, Dixie, Cranky or Candy poses, then copies, realigns and recomposes the frames, adds the palettes, and assembles the code.
- `tools/candy_rig.py`, `tools/candy_poses.py`, `tools/puppet.py`: cut Candy's standing frame into limbs and pose them to make her new frames. `tools/ccmap.py` maps every DK/Diddy animation to a Cranky/Candy one, and `tools/enc.py` packs frames into the 32-tile VRAM slot.
- `tools/funky.py`, `tools/fkmap.py`: Funky's frames (DKC2 art scaled to fit, plus the surfboard) and which DK animation uses which of them.
- `src/hud.asm`, `tools/bananas.py`, `tools/banana_layout.py`, `tools/hud_tiles.py`: collected-banana tracking, the world-map stats and the unlock checks. Every banana in the game is numbered from the level data in your ROM at build time.
- `data/`: frame names and offsets only (no game graphics).

The original code and data are left untouched except for small hooks, and DK & Diddy use the original tables.

## Known limitations

- The Kong choice resets to DK & Diddy when the console is powered off, though it survives soft resets and save/continue within a session.
- Neither DKC2 nor DKC3 has art of Dixie riding an animal or a cart, so she uses one seated pose for those.
- Candy's new frames are made from her standing pose, so they look stiffer than Rare's art. She is shown at two-thirds of her DKC1 size, which is still a little taller than Diddy, while her hitbox stays Diddy-sized.
- Cranky has no swimming, climbing or riding art, so those poses are built from his walk, arms-up and cabin (TNT-throwing) frames. Candy's riding and mine-cart poses are made the same way as her other new frames.
- Funky only has a handful of DKC2 poses (standing, talking, and balancing on his board), so his walk, hurt, swim and climbing poses are made from those, and he always carries his board when jumping. DKC3's Funky art couldn't be located in the ROM's frame tables, so it isn't used. The surfboard move works on foot only, not while riding an animal, in a mine cart or carrying a barrel.
- Some uncommon poses borrow the closest available animation.
- Banana totals count the bananas placed in each level and its bonus rooms. Bananas that only appear after defeating enemies or from barrels aren't included, and they always come back. Copying a file on the file-select screen doesn't copy its level stats or collected bananas.
- On real hardware, pressing L/R on the map may show a one-frame line while the map colours update.

## Credits

- Donkey Kong Country 1–3 © Nintendo / Rare. This is an unofficial fan project, not affiliated with or endorsed by Nintendo or Rare. All game graphics are read from the user's own ROMs at build time.
- [Yoshifanatic1's DKC1 disassembly](https://github.com/Yoshifanatic1/Donkey-Kong-Country-1-Disassembly) (GPL-3.0): routine, RAM and graphic names.
- [DKC1Recomp](https://github.com/elliotttate/DKC1Recomp) (MIT): the Kiddy frame map (`data/kiddy_frames.inc`).
- [DKC2Recomp](https://github.com/elliotttate/DKC2Recomp) and [DKC3Recomp](https://github.com/elliotttate/DKC3Recomp): reference for DKC2/DKC3 animation formats.
- p4plus2's DKC2 disassembly: sprite notes.
- [asar](https://github.com/RPGHacker/asar), [snes9x](https://github.com/snes9xgit/snes9x) and [bsnes](https://github.com/bsnes-emu/bsnes): assembling and testing.

## License

The code in this repository is released under the **GNU GPL v3.0** (see `LICENSE`). Game content is not covered by this license.
