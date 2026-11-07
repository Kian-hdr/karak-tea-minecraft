fn injected(game: &crate::game::Game<'_>, effect: &'static str) -> ::core::ops::ControlFlow<()> {
 if crate::game::karak_tea_milkshake::veto_effect_id(game,effect) {::core::ops::ControlFlow::Break(())}
 else {::core::ops::ControlFlow::Continue(())}
}
