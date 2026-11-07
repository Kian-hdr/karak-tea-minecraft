# Karak Tea native add-on

Private 0.2.0 preview for Horizon `66f3981f522b24c250b21523a70080965b940424`.
Requires the separate Karak Tea content mod. Public release and design acceptance
remain held until qualification finishes.

The add-on changes only tagged `karak_seller` merchants with the recognized
single-ingredient tea offers. Their genuine merchant UI has one active payment
input and a result. Vanilla wire indices remain stable; payment B is unavailable
to placement, pickup, drag, keyboard actions and top-up in the menu engine.
Legacy B contents return to inventory or drop safely rather than disappear.
Other merchants retain their stock two-input UI and pricing.

Recognized prices are regular/iced/decaf=1 emerald, milkshake=2, protein shake=3,
ProMax=8; every result is one cup. Tagged sessions suppress dynamic reputation,
Hero and demand adjustments. Positive player effects themselves are untouched.

The cream chef coat/cap and dark cuffs are editable cuboids in `uniform.rs`.
Stock profession and biome clothing overlays are suppressed only for tagged
sellers, preserving their face and actual profession. The Milkshake protection
uses scoped hooks in `milkshake.rs` to prevent Poison, Nausea and Hunger while
its timer is active. Only existing block texture names are referenced; no raster
textures, Mojang assets or prepared game files are included.

## Files and scope

- `core.rs`: dependency-free policy, strict visual-message decoder, lifecycle
  invalidation and thread-local one-shot operation scope; standalone unit tests.
- `client.rs`: tag checks, server identity markers, genuine single-input drawing,
  and body/head layer adapters.
- `backend.rs`: per-menu secondary-input rejection/refunds and fixed prices.
- `uniform.rs`: editable geometry supplied independently from the UI logic.
- `milkshake.rs`: player-specific protection for the three effects.
- `horizon-mixin.toml`: exact source pin and explicit scoped injections.
- `tools/write_manifest.py`: regenerates the declarative manifest and helpers.

The SDK cannot rewrite the large stock `menu_session` method, which contains a
derived local type. Its pinned callers instead refresh a thread-local operation
intent. The backend click/select hook consumes that intent, marks only that
Menu's secondary payment role Hidden and clears the intent. Normal merchant
callers overwrite it with false. The pinned call graph and actual transaction
tests are part of qualification; compatibility with other native merchant
overrides is not assumed.

## Build without changing a player's instance

Use the launcher's official portable Rust 1.99.1 and Horizon Mixins commit
`e8cd0aa38cffef49cb2e088ef716baa107148c02`. Sources/stage/targets belong under the
ignored project `.build/native_ui/` folder. The official Mixins `plan` and
`apply` commands stage the source; they never patch the original source cache.
On macOS the current SDK requires a fresh output directory when reapplying.

The guarded engine command is:

```sh
python3 native/karak_tea/tools/build_guard.py \
  --cwd .build/native_ui/stage \
  --log evidence/private/native_ui/Native_Build.log \
  --result evidence/private/native_ui/Native_Build.json \
  --floor-gib 6 -- cargo build --locked -p horizon-client \
  --bin horizon-client --profile fast -j2 \
  --target-dir /absolute/project/.build/native_ui/target \
  --config profile.fast.debug=0 \
  --config profile.fast.incremental=false \
  --config profile.fast.lto=false \
  --config profile.fast.package.horizon-client.opt-level=0
```

Put the official portable `cargo`/`rustc` on this command's PATH and use the
private `.build/native_ui/cargo_home`. No global Cargo/launcher settings need to
change. The monitor stops only its own process group if free disk crosses6GiB.
This dev-profile client retains audio/controllers. A controlled showcase
sample is documented in `docs/Validation.md`; larger worlds remain unqualified.

## Supported launcher integration

After qualification, the supported `horizon-launcher import-build` command can
import this already compiled executable on the pinned installed Nightly's game
files. It creates an independent imported version; it does not rebuild it.
Import changes the launcher's selected-version setting, so record and restore
that value through the supported settings command. Create a **new** native
showcase instance, bind it to the imported tag with `instance version`, and
install the matching content pack/fresh showcase world only there. Preserve any
existing worlds and back them up before changing their content mods.

Supply the source `.hnmod` separately for normal supported installs/rebuilds.
Do not redundantly install it in the prebuilt imported instance's native-mod
folder: that would ask the launcher to compile it again. No native-cache
metadata is fabricated by this workflow. Native/unsigned-code trust controls
retain their supported flow.

Compilation alone is not UI, trade, network, uniform or gameplay acceptance.
See the private evidence receipts for the actual qualification state.
