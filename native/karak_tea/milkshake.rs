// Narrow pre-application veto for the milkshake's three protected effects.
// Inject this as game::karak_tea_milkshake. The content pack owns the timer;
// this adapter only reads the actual target player's positive remaining ticks.

use super::Game;
use horizon_client::effects::EffectInstance;

pub const TIMER_OBJECTIVE: &str = "karak_t_milk";

pub fn blocks(effect_id: &str, remaining_ticks: i32) -> bool {
    remaining_ticks > 0
        && matches!(
            effect_id.strip_prefix("minecraft:").unwrap_or(effect_id),
            "poison" | "nausea" | "hunger"
        )
}

pub fn remaining_ticks(game: &Game<'_>) -> i32 {
    if game.player.is_none() {
        return 0;
    }
    // for_player/as_guest swaps the target's actual name into this field.
    // A client-side fallback uses the logged-in profile rather than the
    // generic single-player command holder "Player".
    let holder = game
        .lan_acting_name
        .as_deref()
        .or_else(|| game.remote.as_ref().map(|remote| remote.profile_name.as_str()))
        .unwrap_or_else(|| game.acting_player_name());
    if holder.is_empty() {
        return 0;
    }
    game.score
        .board
        .score(holder, TIMER_OBJECTIVE)
        .map_or(0, |score| score.value)
}

// Call at HEAD of Game::add_player_effect, before effects.add() or any
// absorption/attribute update. Returning false from that method when this
// returns true means no harmful instance enters the player's tick pipeline.
pub fn veto_player_effect(game: &Game<'_>, effect: &EffectInstance) -> bool {
    veto_effect_id(game, effect.id)
}

// Mob/arrow/splash effects enter give_mob_effect directly in this revision,
// bypassing add_player_effect. Its HEAD adapter uses this same narrow policy.
pub fn veto_effect_id(game: &Game<'_>, effect_id: &str) -> bool {
    blocks(effect_id, remaining_ticks(game))
}

#[cfg(test)]
mod tests {
    use super::blocks;

    #[test]
    fn veto_is_exactly_three_vanilla_effects_during_positive_time() {
        for effect in ["poison", "minecraft:poison", "nausea", "minecraft:nausea", "hunger", "minecraft:hunger"] {
            assert!(blocks(effect, 1));
            assert!(blocks(effect, 6000));
            assert!(!blocks(effect, 0));
            assert!(!blocks(effect, -1));
        }
        for effect in ["regeneration", "strength", "night_vision", "fire_resistance", "wither", "slowness", "other:poison"] {
            assert!(!blocks(effect, 6000));
        }
    }
}
