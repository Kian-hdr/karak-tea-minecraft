// Editable, texture-referencing chef uniform for tagged Karak Sellers.
//
// Coordinates are texels (16 per block), +Y up and +Z forward. Body geometry
// uses the feet as its origin. Head geometry is relative to the neck/head
// pivot [0, 24, 0]; the renderer owns head yaw/pitch and the vanilla scale.
// These are clothing overlays, not replacement skin, face, nose or legs.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Attachment {
    Body,
    Head,
}

#[derive(Clone, Copy, Debug)]
pub struct Cube {
    pub from: [f32; 3],
    pub to: [f32; 3],
    pub sprite: &'static str,
    /// RGB multiplicative tint, 0xRRGGBB; renderer supplies opacity.
    pub tint: u32,
    pub attachment: Attachment,
}

const CREAM: u32 = 0xFFF3DC;
const SEAM: u32 = 0xE8DCC6;
const CHARCOAL: u32 = 0x343731;
const CLOTH: &str = "minecraft:block/white_wool";
const JACKET: &str = "minecraft:block/quartz_block_bottom";

pub const CUBES: &[Cube] = &[
    // Cream outer jacket wraps the vanilla long robe so no brown robe shows.
    // Its hem follows the existing robe; exposed lower-leg geometry is untouched.
    Cube { from: [-4.65, 3.2, -3.65], to: [4.65, 24.8, 3.65], sprite: JACKET, tint: CREAM, attachment: Attachment::Body },
    // Narrow front overlap, hem and chest pocket: relief is under half a texel.
    Cube { from: [-0.15, 3.65, 3.66], to: [0.15, 23.0, 3.80], sprite: CLOTH, tint: SEAM, attachment: Attachment::Body },
    Cube { from: [-4.65, 3.2, 3.66], to: [4.65, 3.65, 3.83], sprite: CLOTH, tint: SEAM, attachment: Attachment::Body },
    Cube { from: [2.15, 20.0, 3.67], to: [3.85, 20.35, 3.88], sprite: CLOTH, tint: SEAM, attachment: Attachment::Body },
    // Stand collar: sides/back, plus two small front leaves below the chin.
    // No clothing reaches the nose at forward Z4..6 and body Y23..27.
    Cube { from: [-3.3, 23.35, -3.35], to: [3.3, 24.0, -2.8], sprite: CLOTH, tint: CREAM, attachment: Attachment::Body },
    Cube { from: [-3.3, 23.35, -2.8], to: [-2.8, 24.0, 3.35], sprite: CLOTH, tint: CREAM, attachment: Attachment::Body },
    Cube { from: [2.8, 23.35, -2.8], to: [3.3, 24.0, 3.35], sprite: CLOTH, tint: CREAM, attachment: Attachment::Body },
    Cube { from: [-2.8, 23.35, 3.66], to: [-0.45, 23.95, 3.95], sprite: CLOTH, tint: CREAM, attachment: Attachment::Body },
    Cube { from: [0.45, 23.35, 3.66], to: [2.8, 23.95, 3.95], sprite: CLOTH, tint: CREAM, attachment: Attachment::Body },
    // Jacket sleeves follow the normal folded-arm silhouette. The middle stays
    // open; this is not a solid box spanning the whole chest and folded arms.
    Cube { from: [-8.25, 15.1, -1.95], to: [-4.6, 23.85, 6.85], sprite: CLOTH, tint: CREAM, attachment: Attachment::Body },
    Cube { from: [4.6, 15.1, -1.95], to: [8.25, 23.85, 6.85], sprite: CLOTH, tint: CREAM, attachment: Attachment::Body },
    // Dark cuff edges and two folded gloves; deliberately below face/nose.
    Cube { from: [-4.65, 15.1, 4.25], to: [-3.8, 20.95, 6.7], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    Cube { from: [3.8, 15.1, 4.25], to: [4.65, 20.95, 6.7], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    Cube { from: [-3.8, 15.1, 0.8], to: [-0.12, 20.95, 6.7], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    Cube { from: [0.12, 15.1, 0.8], to: [3.8, 20.95, 6.7], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    // Four visible chef-jacket buttons above the folded hands.
    Cube { from: [-1.5, 21.6, 3.82], to: [-1.05, 22.05, 4.02], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    Cube { from: [1.05, 21.6, 3.82], to: [1.5, 22.05, 4.02], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    Cube { from: [-1.5, 20.35, 3.82], to: [-1.05, 20.8, 4.02], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    Cube { from: [1.05, 20.35, 3.82], to: [1.5, 20.8, 4.02], sprite: CLOTH, tint: CHARCOAL, attachment: Attachment::Body },
    // Soft, low chef cap: close band and a shallow stepped crown. The band
    // starts above the eyes, leaving head-local Y0..8.6 completely unobstructed.
    Cube { from: [-4.65, 8.6, -4.65], to: [4.65, 10.35, 4.65], sprite: CLOTH, tint: SEAM, attachment: Attachment::Head },
    Cube { from: [-5.0, 10.35, -4.8], to: [5.0, 12.0, 4.8], sprite: CLOTH, tint: CREAM, attachment: Attachment::Head },
    Cube { from: [-4.3, 12.0, -4.15], to: [4.45, 13.0, 4.25], sprite: CLOTH, tint: CREAM, attachment: Attachment::Head },
];

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finite_positive_cuboids_with_only_existing_block_sprite_references() {
        assert_eq!(22, CUBES.len());
        for c in CUBES {
            for axis in 0..3 {
                assert!(c.from[axis].is_finite() && c.to[axis].is_finite());
                assert!(c.from[axis] < c.to[axis]);
            }
            assert!(matches!(c.sprite, CLOTH | JACKET));
            assert_eq!(0, c.tint & 0xFF00_0000);
        }
    }

    #[test]
    fn face_nose_and_lower_legs_are_not_replaced_or_covered() {
        for c in CUBES {
            match c.attachment {
                Attachment::Head => {
                    assert!(c.from[1] >= 8.6, "cap must stay above forehead/eyes");
                    assert!(c.to[1] <= 13.0);
                }
                Attachment::Body => {
                    assert!(c.from[1] >= 3.2, "stay above the original robe hem");
                    assert!(c.to[1] <= 24.8);
                    // Nose bounds include body Y23..27, forward Z4..6.
                    assert!(c.to[0] <= -1.0 || c.from[0] >= 1.0 || c.to[1] <= 23.0 || c.to[2] < 4.0);
                }
            }
        }
    }

    #[test]
    fn fitted_width_and_low_cap_preserve_villager_proportions() {
        for c in CUBES {
            let half_width = if c.attachment == Attachment::Head { 5.0 } else { 8.25 };
            assert!(c.from[0] >= -half_width && c.to[0] <= half_width);
            assert!(c.from[2] >= -4.8 && c.to[2] <= 6.85);
        }
        assert_eq!(3, CUBES.iter().filter(|c| c.attachment == Attachment::Head).count());
    }
}
