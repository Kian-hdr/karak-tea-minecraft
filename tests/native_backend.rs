// Compile against the actual staged Horizon client library after the engine
// build; this does not duplicate the merchant arithmetic under test.
extern crate horizon_client_lib as horizon;
use horizon::items::ItemStack;
use horizon::merchant::{ItemCost, MerchantOffer, Session};
use horizon::menu::{karak_tea_core as policy,karak_tea_menu as backend};

fn session(id:&str,price:u32)->Session {
    let o=MerchantOffer {base_cost_a:ItemCost{stack:ItemStack::new("minecraft:emerald",price)},
        cost_b:None,result:ItemStack::new(id,1),uses:0,max_uses:16,reward_exp:true,
        special_price_diff:-20,demand:200,price_multiplier:0.5,xp:0};
    let mut s=Session::new(vec![o],true);s.hero=Some(4);s.reputation=-100;s
}

#[test]
fn all_six_fixed_prices_survive_hero_five_negative_reputation_and_high_demand() {
    for (id,price) in [("karak_tea",1),("iced_karak",1),("decaf_karak",1),
                       ("karak_milkshake",2),("karak_protein_shake",3),("karak_pro_max",8)] {
        let mut s=session(&format!("karak_house:{id}"),price);
        backend::normalize(&mut s);s.update_special_prices();
        let o=&s.offers[0];
        assert_eq!(o.base_cost_a.stack.count,price);assert_eq!(o.special_price_diff,0);
        assert_eq!(o.demand,0);assert_eq!(o.price_multiplier,0.0);
        assert_eq!(s.hero,None);assert_eq!(s.reputation,0);
    }
}

#[test]
fn ordinary_merchant_with_copied_tea_offer_keeps_vanilla_hero_adjustment() {
    let mut s=session("karak_house:karak_pro_max",8);
    let signature=vec![("minecraft:emerald".into(),"karak_house:karak_pro_max".into(),1,false)];
    assert!(!policy::eligible(false,&signature));
    // Ineligible sessions are deliberately left to the real stock calculation.
    s.update_special_prices();
    assert_eq!(s.hero,Some(4));assert_eq!(s.reputation,-100);
    assert_ne!(s.offers[0].special_price_diff,0);
    assert_eq!(s.offers[0].price_multiplier,0.5);assert_eq!(s.offers[0].demand,200);
}
