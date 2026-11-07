// Injected as a public child module of menu.rs, so only this narrow adapter
// touches private menu roles/containers. Ordinary merchants are untouched.
use super::{Env, Kind, Menu, Role, MAIN};

pub fn mark(menu: &mut Menu, enabled: bool) {
    if enabled && menu.kind == Kind::Merchant { menu.slots[1].role = Role::Hidden; }
}

pub fn prepare(menu: &mut Menu, env: &Env<'_>) {
    let intent=super::karak_tea_core::take_operation_intent();
    mark(menu,intent);
    let enabled = menu.kind == Kind::Merchant && matches!(menu.slots[1].role,Role::Hidden);
    configure(menu,env,enabled);
}

pub fn normalize(session: &mut crate::merchant::Session) {
    session.hero = None;
    session.reputation = 0;
    for offer in &mut session.offers {
        if let Some(price) = super::karak_tea_core::fixed_price(&offer.result.item) {
            offer.base_cost_a.stack.count = price;
            offer.special_price_diff = 0;
            offer.demand = 0;
            offer.price_multiplier = 0.0;
        }
    }
}

pub fn configure(menu: &mut Menu, env: &Env<'_>, enabled: bool) {
    if !enabled || menu.kind != Kind::Merchant { return; }
    if let Some(session) = menu.merchant.as_mut() { normalize(session); }
    // Keep wire indices 0/1/2 and inventory3..38 stable. Hidden rejects direct
    // clicks, drag insertion, pickup and shift-click top-up in the stock engine.
    menu.slots[1].role = Role::Hidden;
    // A legacy payment may already be in B. Return it rather than hide/erase it.
    if let Some(mut old) = menu.containers[MAIN][1].take() {
        menu.move_to(env, &mut old, 3, 39, true);
        if old.count > 0 { menu.dropped.push(old); }
    }
    menu.merchant_update(env);
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::items::ItemStack;
    use crate::merchant::{ItemCost, MerchantOffer, Session};
    fn session(result: &str, price: u32) -> Session {
        let offer = MerchantOffer {
            base_cost_a: ItemCost { stack: ItemStack::new("minecraft:emerald",price) },
            cost_b: None, result: ItemStack::new(result,1), uses:0,max_uses:16,
            reward_exp:true,special_price_diff:-7,demand:100,price_multiplier:0.5,xp:0,
        };
        let mut s=Session::new(vec![offer],true);s.hero=Some(4);s.reputation=-100;s
    }
    #[test]
    fn pro_max_keeps_eight_under_hero_five_bad_reputation_and_demand() {
        let mut s=session("karak_house:karak_pro_max",8);
        normalize(&mut s);s.update_special_prices();
        let o=&s.offers[0];
        assert_eq!(o.base_cost_a.stack.count,8);assert_eq!(o.special_price_diff,0);
        assert_eq!(o.demand,0);assert_eq!(o.price_multiplier,0.0);
        assert_eq!(s.hero,None);assert_eq!(s.reputation,0);
    }
    #[test]
    fn other_five_drinks_keep_their_fixed_prices() {
        for (result,price) in [("karak_house:karak_tea",1),("karak_house:iced_karak",1),("karak_house:decaf_karak",1),("karak_house:karak_milkshake",2),("karak_house:karak_protein_shake",3)] {
            let mut s=session(result,price);normalize(&mut s);s.update_special_prices();
            assert_eq!(s.offers[0].base_cost_a.stack.count,price);
            assert_eq!(s.offers[0].special_price_diff,0);
        }
    }
}
