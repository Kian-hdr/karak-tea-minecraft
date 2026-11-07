fn injected(menu: crate::menu::Menu) -> crate::menu::Menu {
 let mut menu=menu;let enabled=crate::menu::karak_tea_core::take_constructor_intent();
 crate::menu::karak_tea_menu::mark(&mut menu,enabled);menu
}
