// Scoped game-facing adapters. Vanilla merchants take the original branches.
use super::{Game, Screen};
use super::native_block_entity_draw::{BlockEntityDraw, CubeFace};
use super::native_mob_draw::NativeMobRender;
use horizon_client::hud::{HudBatch, rgba};
use horizon_client::menu::{karak_tea_core as policy, karak_tea_menu as backend};
use super::trading::MerchantState;

pub fn tagged(game: &Game<'_>, id: u32) -> bool {
    if game.remote.is_some() {
        return policy::client_state().lock().unwrap_or_else(std::sync::PoisonError::into_inner).entity(id);
    }
    game.native_entity(id).and_then(|entity| game.native_entity_tags(entity))
        .is_some_and(|tags| tags.iter().any(|t| t == policy::SELLER_TAG))
}

pub fn terms(session: &horizon_client::merchant::Session) -> bool {
    let offers: Vec<_> = session.offers.iter().map(|o| (
        o.base_cost_a.stack.item.to_string(), o.result.item.to_string(), o.result.count, o.cost_b.is_some()
    )).collect();
    policy::eligible(true, &offers)
}

pub fn state_enabled(game: &Game<'_>, state: &MerchantState) -> bool {
    let identity = if let Some(id) = state.mob { tagged(game, id) } else {
        game.remote.as_ref().and_then(|r| r.menu.as_ref()).is_some_and(|(window, menu)| {
            menu == "minecraft:merchant" && policy::client_state().lock()
                .unwrap_or_else(std::sync::PoisonError::into_inner).window(*window)
        })
    };
    identity && terms(&state.session)
}

pub fn active(game: &Game<'_>) -> bool {
    game.station.as_ref().and_then(|s| s.merchant.as_ref())
        .is_some_and(|state| state_enabled(game, state))
}

pub fn open(game: &mut Game<'_>, mut state: MerchantState) {
    policy::set_operation_intent(false);
    if state_enabled(game, &state) { backend::normalize(&mut state.session); }
    let mut station = super::stations::Station::new_kind(super::stations::Kind::Merchant, [0,0,0]);
    station.merchant = Some(Box::new(state));
    game.station = Some(station);
    game.screen = Screen::Inventory;
    game.capture(false);
    game.right = false;
}

pub fn normalize_and_mark_guest(game: &mut Game<'_>, host: &super::lan::LanHost,
                                conn: u32, guest: &mut super::lan_trading::GuestMerchant) {
    let enabled = guest.merchant.mob.is_some_and(|id| tagged(game,id)) && terms(&guest.merchant.session);
    if enabled { backend::normalize(&mut guest.merchant.session); }
    if let Some(player) = host.hub.guests.iter().find(|g| g.conn == conn) {
        let _ = game.native_net_send_to_player(player.uuid, policy::CHANNEL,
            &policy::encode(policy::Marker::Window(guest.window, enabled)));
        if let Some(id)=guest.merchant.mob {
            let _=game.native_net_send_to_player(player.uuid,policy::CHANNEL,&policy::encode(policy::Marker::Entity(id,enabled)));
        }
    }
}

pub fn guest_active(game: &Game<'_>, host: &super::lan::LanHost, conn: u32) -> bool {
    host.play.get(&conn).and_then(|p|p.merchant.as_ref()).is_some_and(|gm| {
        gm.merchant.mob.is_some_and(|id|tagged(game,id)) && terms(&gm.merchant.session)
    })
}

pub fn receive(game: &Game<'_>, channel: &str, bytes: &[u8]) {
    if game.remote.is_none() || channel != policy::CHANNEL { return; }
    if let Some(marker) = policy::decode(bytes) {
        policy::client_state().lock().unwrap_or_else(std::sync::PoisonError::into_inner).apply(marker);
    }
}

pub fn tracking(game: &mut Game<'_>, player: u128, id: u32, starting: bool) {
    if starting {
        if !game.mobs.iter().any(|m|m.id==id&&m.kind.id=="minecraft:villager") {return;}
        let enabled=tagged(game,id);
        policy::tracks().lock().unwrap_or_else(std::sync::PoisonError::into_inner).start(player,id,enabled);
        if !enabled {return;}
    } else {
        policy::tracks().lock().unwrap_or_else(std::sync::PoisonError::into_inner).stop(player,id);
    }
    {
        let _ = game.native_net_send_to_player(player, policy::CHANNEL,
            &policy::encode(policy::Marker::Entity(id, starting)));
    }
}

pub fn refresh_tracking(game:&mut Game<'_>,id:u32) {
    if game.remote.is_some() || !policy::tracks().lock().unwrap_or_else(std::sync::PoisonError::into_inner).contains(id) {return;}
    if !game.mobs.iter().any(|m|m.id==id&&m.age%20==0) {return;}
    let enabled=tagged(game,id);
    let players=policy::tracks().lock().unwrap_or_else(std::sync::PoisonError::into_inner).refresh(id,enabled);
    for player in players {let _=game.native_net_send_to_player(player,policy::CHANNEL,&policy::encode(policy::Marker::Entity(id,enabled)));}
}

fn label(id: &str) -> String {
    match id {
        "karak_house:iced_karak" => horizon_client::lang::get_or("item.karak_house.iced_karak","Iced Karak"),
        "karak_house:decaf_karak" => horizon_client::lang::get_or("item.karak_house.decaf_karak","Decaf Karak"),
        "karak_house:karak_pro_max" => horizon_client::lang::get_or("item.karak_house.karak_pro_max","Karak ProMax"),
        "karak_house:karak_milkshake" => horizon_client::lang::get_or("item.karak_house.karak_milkshake","Karak Milkshake"),
        "karak_house:karak_protein_shake" => horizon_client::lang::get_or("item.karak_house.karak_protein_shake","Karak Protein Shake"),
        _ => horizon_client::lang::get_or("item.karak_house.karak_tea","Karak Tea"),
    }
}

pub fn draw(game: &mut Game<'_>, batch: &mut HudBatch) -> bool {
    if !active(game) { return false; }
    let (ox,oy) = game.inventory_origin(batch);
    let state = game.station.as_ref().and_then(|s| s.merchant.as_ref()).expect("scoped merchant");
    let offers = state.session.offers.clone();
    let selected = state.session.selection_hint.min(offers.len()-1);
    let scroll = state.scroll;
    let name = state.name.clone().unwrap_or_else(|| horizon_client::lang::get_or("entity.karak_house.karak_seller","Karak Seller"));
    super::screen_info::name_container(||name.clone());
    let atlas = &game.gui.atlas;
    batch.fill(atlas,0.0,0.0,batch.width,batch.height,rgba(16,16,16,160));
    // Draw a genuine single-input panel; the stock two-slot texture is never drawn.
    batch.fill(atlas,ox-51.0,oy-1.0,278.0,168.0,0xFF373737);
    batch.fill(atlas,ox-50.0,oy,276.0,166.0,0xFFC6C6C6);
    batch.fill(atlas,ox+49.0,oy+15.0,1.0,146.0,0xFF888888);
    batch.text(atlas,&name,ox+55.0,oy+6.0,0xFF404040,false);
    batch.text(atlas,&horizon_client::lang::get_or("merchant.trades","Trades"),ox-44.0,oy+6.0,0xFF404040,false);
    batch.text(atlas,&horizon_client::lang::get_or("container.inventory","Inventory"),ox+58.0,oy+72.0,0xFF404040,false);
    batch.text(atlas,&label(&offers[selected].result.item),ox+70.0,oy+22.0,0xFF404040,false);
    batch.text(atlas,"->",ox+128.0,oy+41.0,0xFF404040,false);
    for (i,offer) in offers.iter().enumerate().skip(scroll).take(7) {
        let y = oy+18.0+((i-scroll)*20) as f32;
        batch.fill(&game.gui.atlas,ox-46.0,y-1.0,88.0,20.0,if i==selected {0xFF999999}else{0xFFB3B3B3});
        game.draw_item(batch,&offer.cost_a(game.items()),ox-40.0,y);
        game.draw_item(batch,&offer.result,ox+22.0,y);
        batch.text(&game.gui.atlas,"->",ox-5.0,y+4.0,0xFF404040,false);
    }
    let slots = game.slots();
    let drag = game.drag_view();
    for &id in &slots {
        let (x,y) = game.slot_position(id);
        batch.fill(&game.gui.atlas,ox+x-1.0,oy+y-1.0,18.0,18.0,0xFF373737);
        batch.fill(&game.gui.atlas,ox+x,oy+y,16.0,16.0,0xFF8B8B8B);
    }
    game.draw_hovered_slot_highlight(batch,false,ox,oy);
    for id in slots {
        let (x,y) = game.slot_position(id);
        let stack = game.slot_mut(id).clone();
        game.draw_slot_item(batch,drag.as_ref(),id,&stack,ox+x,oy+y);
    }
    game.draw_hovered_slot_highlight(batch,true,ox,oy);
    let tooltip = game.slot_at(batch,game.cursor.0,game.cursor.1).and_then(|id| game.slot_mut(id).clone());
    game.draw_carried(batch);
    if let Some(stack) = tooltip {
        game.draw_stack_tooltip(batch,&stack,game.cursor.0,game.cursor.1);
    }
    true
}

pub fn uniform(game: &Game<'_>, mob: &NativeMobRender<'_>, draw: &mut BlockEntityDraw) {
    if mob.baby || mob.kind != "minecraft:villager" || !tagged(game,mob.id) { return; }
    use super::karak_tea_uniform::{Attachment,CUBES};
    for cube in CUBES {
        draw.push();
        if matches!(cube.attachment,Attachment::Head) {
            draw.translate([0.0,1.5,0.0]);
            draw.rotate_about([0.0,1.0,0.0],-mob.head_yaw,[0.0;3]);
            draw.rotate_about([1.0,0.0,0.0],mob.pitch,[0.0;3]);
        }
        let sprite=cube.sprite.strip_prefix("minecraft:").unwrap_or(cube.sprite);
        let faces = std::array::from_fn(|_| Some(CubeFace {sprite,uv:Some([0.0,0.0,16.0,16.0])}));
        game.native_draw_cube(draw,cube.from,cube.to,faces,cube.tint);
        draw.pop();
    }
}

// Populate the renderer's scoped identity before vanilla layers are selected.
// This never replaces the base model or changes a villager's actual job.
pub fn render_marker(game:&Game<'_>,mob:&NativeMobRender<'_>) {
 if mob.kind!="minecraft:villager" {return;}
 let enabled=tagged(game,mob.id);
 policy::client_state().lock().unwrap_or_else(std::sync::PoisonError::into_inner)
  .apply(policy::Marker::Entity(mob.id,enabled));
}
