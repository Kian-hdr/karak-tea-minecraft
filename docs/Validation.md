# Validation status

Target: Horizon `nightly-2026-11-05-66f3981`, content API0.2. Tests ran on an Apple Silicon Mac. This is a private review candidate, not a published release. The owner selected the unchanged standard client: native-only UI, uniform, exact higher-price protection and first-tick Milkshake immunity below describe the earlier native test candidate, not the installed standard-client behavior.

## Automated checks

The current default suite runs 42 tests, with five opt-in live tests skipped. Separate isolated live tests cover the behaviors below; a skipped test is not itself evidence of a pass.

## Gameplay

Actual in-game tests covered:

- One emerald removed for each cup purchased; copper refused.
- Unchanged price with Hero of the Village V and changed demand.
- Sixteen-cup stock replenished by the seller’s daily server function after a day transition.
- Free cup on real interaction, once per eligible seller, with no reward from merely looking.
- Two nearby sellers: only the clicked seller loses its free offer.
- Saved claimed/unclaimed state through reload, unload and complete game reopen.
- Daily transition and no reroll from moving the clock backward.
- Six drink varieties with independent refresh and expiry, additive stacking, milk and death clearing. The native Milkshake protection was tested against commands and a pufferfish attack.

Simultaneous multiplayer claiming is not qualified. The10% probability is a uniform1..10 roll with one eligible result; the tests do not establish a population estimate from a large random campaign.

## Natural village generation

One deterministic seed and five fixed search anchors per village style produced25 distinct natural starts. The final raised-stair design appeared in21/25(84%), with no village containing more than one Karak House. By style: plains5/5, desert1/5, savanna5/5, taiga5/5, snowy5/5. This satisfies the bounded80% acceptance target; it is not a claim that84% of all seeds or each village type will contain a shop.

All21 generated house connections were physically traversed with auto-jump disabled and without jump commands, across all four horizontal rotations. All315 landing blocks and63 front stairs retained their expected materials/orientations after natural generation. Unmodified vanilla roads farther from the authored entrance may still have ordinary terrain steps.

## Design review and showcase

The owner approved the latest cup design and asked to finish the mod. The showcase is a separate inspection world; it does not replace the natural-generation sample. The 0.2.0 showcase is installed in a separate local instance and reopens with the pack loaded. Five sellers and their regular emerald inputs were observed after reopening. Five-house entry and purchase checks passed in an isolated copy; see the paired-door qualification below.

## Asset boundaries

The pack references the player's existing Minecraft textures; it does not contain them. House and cup models are editable geometry. No generated raster imagery is included. Public release remains held for review.

## Remaining acceptance

- The latest cup design was approved by the owner; later feedback can be applied to the personal preview.
- The complete five-seller playthrough used an isolated offscreen copy; an owner playthrough of the installed showcase remains welcome.
- A visible-window showcase flight was sampled; verify performance in a larger representative world if support for that workload is claimed.
- Superseded Karak instances were moved to Trash after isolated functional verification. Their three worlds have separate integrity-checked backups; the default Horizon instance remains.
- Keep the repository private until the requested testing and design review are complete. Public publication has not occurred.

## Paired entrance doors

The 0.2.0 content pack now pairs the two entry leaves when either plate is pressed. In isolated survival tests with auto-jump disabled, 20 approaches across the five showcase styles and 16 approaches across four naturally generated rotations passed. Powered save/reload passed, and an unrelated ordinary double-door control retained normal behavior. The five structure templates were unchanged from the tested fixture. This is not a new 25-village frequency sample.

A 10-second stationary visible-window sample of the final native client on the target Apple Silicon Mac, in a separate showcase copy with render distance 8, reported approximately 120 FPS (1201 frames, 119.999 average FPS). The test session closed cleanly. This single sample does not establish performance while walking, in large villages, or on other machines.

A separate 20-second visible-window camera flight across the five-house showcase at render distance 8 reported 119.99 average FPS, 115.26 FPS 1% low, and 20.02 ms maximum smoothed server tick time on the same Mac. This is one controlled scene, not a guarantee for larger worlds or other hardware.

## Content-mod compatibility sample

On unchanged Horizon revision 66f3981, Karak Tea was loaded alongside one independent synthetic content mod. Both items worked before and after reload, and two naturally generated plains villages each contained one Karak House, the other mod's stall, and vanilla structures. This is a bounded compatibility check, not a guarantee for arbitrary modpacks. GUI-only pixel icons and their 3D held-model fallback were also checked in the stock client.

The exact installed stock-client pack (`b071049419ce925ffe0aa31e2a996c245f003f1223a98da5d9a5ceecd2b3fd60`) was also tested in a disposable copy of the saved showcase. All six base-price purchases and drink effects passed, and seller state, offers and purchased inventory persisted after save/reopen. Milk cleared the effects. This test did not qualify first-tick Milkshake poison immunity or Hero-proof prices, which require native support.

## Standard-client seller clothing

The owner approved a cream cap and vanilla butcher apron as the stock-client approximation. In a disposable world, the cap, actual purchase, daily restock, non-dropping cap, save/reload and one-time migration were tested. Existing headgear, offer data and giveaway scores were preserved; ordinary villagers were unchanged. This is not the originally pictured full cream coat and gloves. A seller with an occupied head slot keeps that headgear.

The installed standard-client pack was checked in the owner's existing showcase after a fresh backup: all five tagged sellers had the cap, butcher profession, and one-emerald regular input. After save, quit, and reopen, all five caps and regular inputs persisted. No trade or player movement was performed in the owner's world; actual transactions and effects were tested in disposable copies.
