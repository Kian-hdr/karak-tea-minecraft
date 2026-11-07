fn injected(game: &mut crate::game::Game<'_>, batch: &mut horizon_client::hud::HudBatch) -> ::core::ops::ControlFlow<bool> {
 if crate::game::karak_tea::draw(game,batch) { ::core::ops::ControlFlow::Break(true) }
 else { ::core::ops::ControlFlow::Continue(()) }
}
