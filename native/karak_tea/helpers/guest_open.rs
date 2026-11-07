fn injected(game: &mut crate::game::Game<'_>, host: &crate::game::lan::LanHost, conn: u32, value: crate::game::lan_trading::GuestMerchant) -> crate::game::lan_trading::GuestMerchant {
 let mut value=value;crate::game::karak_tea::normalize_and_mark_guest(game,host,conn,&mut value);value
}
