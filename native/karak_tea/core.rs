// Dependency-free policy and validated server-to-client visual markers.
// This exact file is injected as horizon_client_lib::menu::karak_tea_core.
use std::collections::{BTreeMap,BTreeSet};
use std::cell::Cell;
use std::sync::{Mutex, OnceLock};

pub const CHANNEL: &str = "karak_tea_native:state";
pub const SELLER_TAG: &str = "karak_seller";

pub fn fixed_price(result: &str) -> Option<u32> {
    match result {
        "karak_house:karak_tea" | "karak_house:iced_karak" | "karak_house:decaf_karak" => Some(1),
        "karak_house:karak_pro_max" => Some(8),
        "karak_house:karak_milkshake" => Some(2),
        "karak_house:karak_protein_shake" => Some(3),
        _ => None,
    }
}

// The tag is indispensable: a copied offer on another merchant never scopes it in.
pub fn eligible(tagged: bool, offers: &[(String, String, u32, bool)]) -> bool {
    tagged && !offers.is_empty() && offers.iter().all(|(input, result, count, second)| {
        input == "minecraft:emerald" && *count == 1 && !second && fixed_price(result).is_some()
    })
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Marker { Entity(u32, bool), Window(i32, bool) }

pub fn encode(marker: Marker) -> [u8; 6] {
    let (op, id) = match marker {
        Marker::Entity(id, true) => (1, id),
        Marker::Entity(id, false) => (2, id),
        Marker::Window(id, true) => (3, id as u32),
        Marker::Window(id, false) => (4, id as u32),
    };
    let b = id.to_le_bytes();
    [1, op, b[0], b[1], b[2], b[3]]
}

pub fn decode(bytes: &[u8]) -> Option<Marker> {
    let [1, op, a, b, c, d] = bytes else { return None };
    let id = u32::from_le_bytes([*a, *b, *c, *d]);
    match op {
        1 | 2 if id > 0 => Some(Marker::Entity(id, *op == 1)),
        3 | 4 if id <= i32::MAX as u32 => Some(Marker::Window(id as i32, *op == 3)),
        _ => None,
    }
}

#[derive(Default)]
pub struct ClientState {
    entities: BTreeSet<u32>,
    window: Option<(i32, bool)>,
}
impl ClientState {
    pub fn apply(&mut self, marker: Marker) {
        match marker {
            Marker::Entity(id, true) if self.entities.len() < 4096 => { self.entities.insert(id); }
            Marker::Entity(id, false) => { self.entities.remove(&id); }
            Marker::Window(id, enabled) => self.window = Some((id, enabled)),
            _ => {}
        }
    }
    pub fn entity(&self, id: u32) -> bool { self.entities.contains(&id) }
    pub fn window(&self, id: i32) -> bool { self.window == Some((id, true)) }
}

pub fn client_state() -> &'static Mutex<ClientState> {
    static STATE: OnceLock<Mutex<ClientState>> = OnceLock::new();
    STATE.get_or_init(Default::default)
}

pub fn clear_client() {
    *client_state().lock().unwrap_or_else(std::sync::PoisonError::into_inner) = ClientState::default();
    set_operation_intent(false);
}

// Every pinned game entry to menu_session and the LAN merchant operation
// refreshes this one-shot tagged-operation intent. The first authoritative
// click/select consumes and clears it; subsequent clicks use that Menu's
// Hidden role. Normal merchant entry points overwrite it with false.
std::thread_local! { static OPERATION_INTENT: Cell<bool> = const { Cell::new(false) }; }
pub fn set_operation_intent(enabled: bool) { OPERATION_INTENT.with(|v|v.set(enabled)); }
pub fn take_operation_intent() -> bool { OPERATION_INTENT.with(|v|v.replace(false)) }

pub fn reset_world() {
    clear_client();
}

#[derive(Default)]
pub struct Tracks(BTreeMap<u32,(bool,BTreeSet<u128>)>);
impl Tracks {
    pub fn start(&mut self, player:u128, entity:u32, tagged:bool) {
        let entry=self.0.entry(entity).or_insert_with(||(tagged,BTreeSet::new()));
        entry.0=tagged;entry.1.insert(player);
    }
    pub fn stop(&mut self, player:u128, entity:u32) {
        if let Some(entry)=self.0.get_mut(&entity) {entry.1.remove(&player);if entry.1.is_empty(){self.0.remove(&entity);}}
    }
    pub fn contains(&self,id:u32)->bool {self.0.contains_key(&id)}
    pub fn refresh(&mut self,id:u32,tagged:bool)->Vec<u128> {
        let Some(entry)=self.0.get_mut(&id) else{return Vec::new()};
        let notify=tagged||entry.0!=tagged;entry.0=tagged;
        if notify {entry.1.iter().copied().collect()} else {Vec::new()}
    }
}
pub fn tracks()->&'static Mutex<Tracks> {static T:OnceLock<Mutex<Tracks>>=OnceLock::new();T.get_or_init(Default::default)}
pub fn reset_server() {*tracks().lock().unwrap_or_else(std::sync::PoisonError::into_inner)=Tracks::default();set_operation_intent(false);}

#[cfg(test)]
mod tests {
    use super::*;
    fn offer(id: &str) -> (String, String, u32, bool) {
        ("minecraft:emerald".into(), id.into(), 1, false)
    }
    #[test]
    fn tag_is_required_even_for_identical_tea_offers() {
        let offers = [offer("karak_house:karak_tea")];
        assert!(!eligible(false, &offers));
        assert!(eligible(true, &offers));
    }
    #[test]
    fn six_drinks_have_explicit_fixed_prices() {
        assert_eq!(fixed_price("karak_house:karak_pro_max"), Some(8));
        assert_eq!(fixed_price("karak_house:karak_milkshake"), Some(2));
        assert_eq!(fixed_price("karak_house:karak_protein_shake"), Some(3));
        for id in ["karak_tea", "iced_karak", "decaf_karak"] {
            assert_eq!(fixed_price(&format!("karak_house:{id}")), Some(1));
        }
        assert_eq!(fixed_price("minecraft:potion"), None);
    }
    #[test]
    fn second_payment_and_foreign_goods_fail_closed() {
        let mut o = offer("karak_house:karak_tea"); o.3 = true;
        assert!(!eligible(true, &[o]));
        assert!(!eligible(true, &[offer("minecraft:bread")]));
        assert!(!eligible(true, &[]));
    }
    #[test]
    fn protocol_is_versioned_and_strictly_sized() {
        for marker in [Marker::Entity(12, true), Marker::Entity(12, false), Marker::Window(31, true), Marker::Window(31, false)] {
            assert_eq!(decode(&encode(marker)), Some(marker));
        }
        assert_eq!(decode(&[2, 1, 1, 0, 0, 0]), None);
        assert_eq!(decode(&[1, 9, 1, 0, 0, 0]), None);
        assert_eq!(decode(&[1, 1, 1, 0, 0, 0, 0]), None);
        assert_eq!(decode(&[1, 1, 0, 0, 0, 0]), None);
    }
    #[test]
    fn markers_never_apply_to_other_entities_or_windows() {
        let mut s = ClientState::default();
        s.apply(Marker::Entity(2, true));
        assert!(s.entity(2)); assert!(!s.entity(3));
        s.apply(Marker::Entity(2, false)); assert!(!s.entity(2));
        s.apply(Marker::Window(5, true)); assert!(s.window(5)); assert!(!s.window(6));
        s.apply(Marker::Window(6, false)); assert!(!s.window(5)); assert!(!s.window(6));
    }
    #[test]
    fn operation_intent_is_one_shot_overwritten_and_thread_local() {
        set_operation_intent(true);assert!(take_operation_intent());assert!(!take_operation_intent());
        set_operation_intent(true);set_operation_intent(false);assert!(!take_operation_intent());
        set_operation_intent(true);
        assert!(!std::thread::spawn(take_operation_intent).join().unwrap());
        assert!(take_operation_intent());
    }
    #[test]
    fn world_reset_drops_reusable_entity_and_window_ids() {
        {let mut s=client_state().lock().unwrap();s.apply(Marker::Entity(2,true));s.apply(Marker::Window(5,true));}
        set_operation_intent(true);reset_world();
        let s=client_state().lock().unwrap();assert!(!s.entity(2));assert!(!s.window(5));
        assert!(!take_operation_intent());
    }
    #[test]
    fn server_tracking_notifies_tag_removal_and_forgets_departed_players() {
        let mut t=Tracks::default();t.start(10,7,true);t.start(11,7,true);
        assert_eq!(t.refresh(7,false),vec![10,11]);assert!(t.refresh(7,false).is_empty());
        t.stop(10,7);assert_eq!(t.refresh(7,true),vec![11]);t.stop(11,7);assert!(!t.contains(7));
    }
}
