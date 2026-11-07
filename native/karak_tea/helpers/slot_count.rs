fn injected(game: &crate::game::Game<'_>) -> ::core::ops::ControlFlow<Option<usize>> {
 if crate::game::karak_tea::active(game) {::core::ops::ControlFlow::Break(Some(38))}
 else {::core::ops::ControlFlow::Continue(())}
}
