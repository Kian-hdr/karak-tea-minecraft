from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
manifest='''[mod]
id = "karak_tea_native"
version = "0.2.0"
priority = 100

[compatibility]
horizon_revision = "66f3981f522b24c250b21523a70080965b940424"

'''
for ident,file,name,source,vis in [('policy','crates/horizon-client/src/menu.rs','karak_tea_core','core.rs','pub'),('backend','crates/horizon-client/src/menu.rs','karak_tea_menu','backend.rs','pub'),('game','crates/horizon-client/src/game.rs','karak_tea','client.rs','pub(crate)'),('uniform','crates/horizon-client/src/game.rs','karak_tea_uniform','uniform.rs','pub(crate)'),('milkshake','crates/horizon-client/src/game.rs','karak_tea_milkshake','milkshake.rs','pub(crate)')]:
 manifest+=f'[[module]]\nid = "module_{ident}"\nfile = "{file}"\nname = "{name}"\nsource = "{source}"\nvisibility = "{vis}"\n\n'
def add(ident,kind,target,params,body,selector=None,cancel=False,hook=False):
 global manifest
 file='helpers/'+ident+'.rs';signature=', '.join(f'{n}: {t}' for n,t,v in params)
 (ROOT/file).write_text(f'fn injected({signature})'+body+'\n')
 manifest+=f'[[injection]]\nid = "{ident}"\nkind = "{kind}"\n'
 if hook:manifest+=f'hook = "{target}"\nhook_version = 1\n'
 else:manifest+=f'target = "{target}"\n'
 manifest+=f'helper = "{file}"\n'
 if selector:manifest+=f'selector = "{selector}"\nrequire = 1\nordinal = 0\n'
 if cancel:manifest+='cancellable = true\n'
 manifest+='bindings = ['+', '.join('{ name = '+json.dumps(n)+', ty = '+json.dumps(t)+', value = '+json.dumps(v)+' }' for n,t,v in params)+']\n\n'
game=('game',"&crate::game::Game<'_>",'&*self');gm=('game',"&mut crate::game::Game<'_>",'&mut *self')
add('open','OVERWRITE',"horizon_client::game::trading::Game<'_>::open_merchant_state",[gm,('state','crate::game::trading::MerchantState','state')],''' { crate::game::karak_tea::open(game,state); }''')
add('draw','HEAD',"horizon_client::game::trading::Game<'_>::draw_merchant",[gm,('batch','&mut horizon_client::hud::HudBatch','&mut *batch')],''' -> ::core::ops::ControlFlow<bool> {
 if crate::game::karak_tea::draw(game,batch) { ::core::ops::ControlFlow::Break(true) }
 else { ::core::ops::ControlFlow::Continue(()) }
}''',cancel=True)
add('slots','HEAD',"horizon_client::game::stations::Game<'_>::station_slots",[game],''' -> ::core::ops::ControlFlow<Option<Vec<usize>>> {
 if crate::game::karak_tea::active(game) {
  let mut slots:Vec<usize>=(0..36).collect();slots.extend([600,650]);
  ::core::ops::ControlFlow::Break(Some(slots))
 } else {::core::ops::ControlFlow::Continue(())}
}''',cancel=True)
add('slot_count','HEAD',"horizon_client::game::stations::Game<'_>::station_slot_count",[game],''' -> ::core::ops::ControlFlow<Option<usize>> {
 if crate::game::karak_tea::active(game) {::core::ops::ControlFlow::Break(Some(38))}
 else {::core::ops::ControlFlow::Continue(())}
}''',cancel=True)
for method in ['menu_ops','drag_view','quick_craft_accepts','inventory_press']:
 add('local_'+method,'HEAD',f"horizon_client::game::Game<'_>::{method}",[game],''' { horizon_client::menu::karak_tea_core::set_operation_intent(crate::game::karak_tea::active(game)); }''')
add('local_select','HEAD',"horizon_client::game::trading::Game<'_>::try_move_items",[game],''' { horizon_client::menu::karak_tea_core::set_operation_intent(crate::game::karak_tea::active(game)); }''')
for module,methods in [('remote',['remote_menu_ops','remote_quick_move_all']),('recipe_book',['book_available','place_recipe']),('remote_stations',['remote_station_slot_changed']),('tweaks',['tweak_result','tweak_takes_one','tweak_landing']),('stations',['close_station','stonecutter_recipe_click']),('loom',['loom_button'])]:
 for method in methods:
  add('scope_'+method,'HEAD',f"horizon_client::game::{module}::Game<'_>::{method}",[game],''' { horizon_client::menu::karak_tea_core::set_operation_intent(crate::game::karak_tea::active(game)); }''')
add('guest_backend','HEAD',"horizon_client::game::lan_trading::Game<'_>::lan_merchant_op",[game,('host','&crate::game::lan::LanHost','&*host'),('conn','u32','conn')],''' { horizon_client::menu::karak_tea_core::set_operation_intent(crate::game::karak_tea::guest_active(game,host,conn)); }''')
add('guest_open','MODIFY_VARIABLE',"horizon_client::game::lan_trading::Game<'_>::lan_open_merchant",[gm,('host','&crate::game::lan::LanHost','&*host'),('conn','u32','conn'),('value','crate::game::lan_trading::GuestMerchant','$value')],''' -> crate::game::lan_trading::GuestMerchant {
 let mut value=value;crate::game::karak_tea::normalize_and_mark_guest(game,host,conn,&mut value);value
}''')
manifest+='variable = { name = "gm", ordinal = 0, at = "STORE" }\nrequire = 1\nordinal = 0\n\n'
for ident,method in [('click_backend','click'),('select_backend','merchant_select')]:
 add(ident,'HEAD',f'horizon_client_lib::menu::Menu::{method}',[('menu','&mut crate::menu::Menu','&mut *self'),('env',"&crate::menu::Env<'_>",'env')],''' { crate::menu::karak_tea_menu::prepare(menu,env); }''')
add('network','HEAD','net_from_server',[game,('channel','&str','channel'),('data','&[u8]','data')],''' { crate::game::karak_tea::receive(game,channel,data); }''',hook=True)
for ident,hook in [('disconnect','client_disconnecting'),('level_load','client_level_load'),('level_unload','client_level_unload')]:
 add(ident,'HEAD',hook,[],''' { horizon_client::menu::karak_tea_core::reset_world(); }''',hook=True)
add('server_world','HEAD','world_lifecycle',[('phase','horizon_client::mod_api::WorldPhase','phase')],''' {
 use horizon_client::mod_api::WorldPhase;
 if matches!(phase,WorldPhase::WorldOpenReady|WorldPhase::WorldCloseFinal|WorldPhase::WorldCloseFailed|WorldPhase::WorldOpenFailed) {horizon_client::menu::karak_tea_core::reset_server();}
 horizon_client::menu::karak_tea_core::set_operation_intent(false);
}''',hook=True)
add('tag_refresh','HEAD','entity_tick_post',[gm,('entity','u32','entity')],''' {crate::game::karak_tea::refresh_tracking(game,entity);}''',hook=True)
for name,start in [('player_start_tracking',True),('player_stop_tracking',False)]:
 add(name,'HEAD',name,[gm,('player','u128','player'),('entity','u32','entity')],f' {{ crate::game::karak_tea::tracking(game,player,entity,{str(start).lower()}); }}',hook=True)
add('layer_listened','HEAD','player_render_listened',[('listened','&mut bool','&mut *listened')],''' { *listened=true; }''',hook=True)
add('uniform','HEAD','mob_layer',[game,('mob',"&crate::game::native_mob_draw::NativeMobRender<'_>",'mob'),('draw','&mut crate::game::native_block_entity_draw::BlockEntityDraw','&mut *draw')],''' { crate::game::karak_tea::uniform(game,mob,draw); }''',hook=True)
add('milkshake_veto','HEAD',"horizon_client::game::potions::Game<'_>::add_player_effect",[game,('effect','&horizon_client::effects::EffectInstance','&effect')],''' -> ::core::ops::ControlFlow<bool> {
 if crate::game::karak_tea_milkshake::veto_player_effect(game,effect) {::core::ops::ControlFlow::Break(false)}
 else {::core::ops::ControlFlow::Continue(())}
}''',cancel=True)
add('milkshake_mob_veto','HEAD',"horizon_client::game::creatures::Game<'_>::give_mob_effect",[game,('effect',"&'static str",'effect')],''' -> ::core::ops::ControlFlow<()> {
 if crate::game::karak_tea_milkshake::veto_effect_id(game,effect) {::core::ops::ControlFlow::Break(())}
 else {::core::ops::ControlFlow::Continue(())}
}''',cancel=True)
add('render_identity','HEAD','mob_submit',[game,('mob',"&crate::game::native_mob_draw::NativeMobRender<'_>",'mob')],''' {crate::game::karak_tea::render_marker(game,mob);}''',hook=True)
add('karak_clothing_layers','HEAD','horizon_client_lib::mobs::render::layers',[('mob','&crate::mobs::Mob','m')],''' -> ::core::ops::ControlFlow<Vec<Layer>> {
 let ours=mob.species()==crate::mobs::Species::Villager && crate::menu::karak_tea_core::client_state().lock().unwrap_or_else(std::sync::PoisonError::into_inner).entity(mob.id);
 if ours {::core::ops::ControlFlow::Break(Vec::new())} else {::core::ops::ControlFlow::Continue(())}
}''',cancel=True)
(ROOT/'horizon-mixin.toml').write_text(manifest.rstrip() + '\n')
print('Wrote scoped manifest and4supportmodules')
