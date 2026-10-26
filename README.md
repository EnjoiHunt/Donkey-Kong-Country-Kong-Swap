# Donkey Kong Country: Kong Swap

A ROM hack of **Donkey Kong Country** (SNES, USA v1.0) that adds **Kiddy Kong** (from DKC3) and **Dixie Kong** (from DKC2) as a second playable pair. Press **L or R on the world map** to switch between **DK & Diddy** and **Kiddy & Dixie**.

![Switching pairs on the world map](docs/images/switching.png)

## Features

- **Switch pairs any time on the world map** with L or R. DK & Diddy stay exactly as in the original game.
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
![World map sprites](docs/images/world_map.png)
![Level-complete faces](docs/images/level_faces.png)

## Playing it

1. Get a **clean, headerless** dump of *Donkey Kong Country (USA) v1.0* from a cartridge you own.
   SHA-256: `fa8cacf5bbfc39ee6bbaa557adf89133d60d42f6cf9e1db30d5a36a469f74d15`
2. Apply [`patches/dkc1_kong_swap_v1.0.bps`](patches/dkc1_kong_swap_v1.0.bps) (recommended, because it checks that you used the right ROM) or [`patches/dkc1_kong_swap_v1.0.ips`](patches/dkc1_kong_swap_v1.0.ips) (for patchers that only support IPS) with [Floating IPS](https://www.smwcentral.net/?p=section&a=details&id=11474) or [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/).
3. Play in any accurate SNES emulator (tested in snes9x and bsnes).

The patched ROM is 8 MB (ExHiROM).

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

- `src/kong_swap.asm`: all new 65816 code (assembled with asar). It covers the pair switch, the alternate frame-table and palette lookups, the map hooks, the helicopter spin, the ground pound, held-barrel placement and the level-complete faces.
- `tools/build.py`: expands DKC1 to 8 MB ExHiROM. It builds a second sprite-frame table where every DK/Diddy pose points at a matching Kiddy/Dixie pose, then copies, realigns and recomposes the frames, adds the palettes, and assembles the code.
- `data/`: frame names and offsets only (no game graphics).

The original code and data are left untouched except for small hooks, and DK & Diddy use the original tables.

## Known limitations

- The pair choice resets to DK & Diddy when the console is powered off, though it survives soft resets and save/continue within a session.
- Neither DKC2 nor DKC3 has art of Dixie riding an animal or a cart, so she uses one seated pose for those.
- Some uncommon poses borrow the closest available animation.
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
