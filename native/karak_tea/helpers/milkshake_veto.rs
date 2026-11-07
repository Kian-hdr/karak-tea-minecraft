fn injected(game: &crate::game::Game<'_>, effect: &horizon_client::effects::EffectInstance) -> ::core::ops::ControlFlow<bool> {
 if crate::game::karak_tea_milkshake::veto_player_effect(game,effect) {::core::ops::ControlFlow::Break(false)}
 else {::core::ops::ControlFlow::Continue(())}
}
