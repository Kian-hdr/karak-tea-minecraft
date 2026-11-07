fn injected(mob: &crate::mobs::Mob) -> ::core::ops::ControlFlow<Vec<Layer>> {
 let ours=mob.species()==crate::mobs::Species::Villager && crate::menu::karak_tea_core::client_state().lock().unwrap_or_else(std::sync::PoisonError::into_inner).entity(mob.id);
 if ours {::core::ops::ControlFlow::Break(Vec::new())} else {::core::ops::ControlFlow::Continue(())}
}
