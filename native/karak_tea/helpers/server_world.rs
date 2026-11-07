fn injected(phase: horizon_client::mod_api::WorldPhase) {
 use horizon_client::mod_api::WorldPhase;
 if matches!(phase,WorldPhase::WorldOpenReady|WorldPhase::WorldCloseFinal|WorldPhase::WorldCloseFailed|WorldPhase::WorldOpenFailed) {horizon_client::menu::karak_tea_core::reset_server();}
 horizon_client::menu::karak_tea_core::set_operation_intent(false);
}
