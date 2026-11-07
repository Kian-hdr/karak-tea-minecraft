fn injected(game: &crate::game::Game<'_>) -> ::core::ops::ControlFlow<Option<Vec<usize>>> {
 if crate::game::karak_tea::active(game) {
  let mut slots:Vec<usize>=(0..36).collect();slots.extend([600,650]);
  ::core::ops::ControlFlow::Break(Some(slots))
 } else {::core::ops::ControlFlow::Continue(())}
}
