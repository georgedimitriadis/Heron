from dearpygui.core import *
import os


def set_style(heron_path):
    set_style_window_padding(8.00, 8.00)
    set_style_frame_padding(4.00, 3.00)
    set_style_item_spacing(8.00, 4.00)
    set_style_item_inner_spacing(4.00, 4.00)
    set_style_touch_extra_padding(0.00, 0.00)
    set_style_indent_spacing(21.00)
    set_style_scrollbar_size(14.00)
    set_style_grab_min_size(10.00)
    set_style_window_border_size(1.00)
    set_style_child_border_size(1.00)
    set_style_popup_border_size(1.00)
    set_style_frame_border_size(1.00)
    set_style_tab_border_size(0.00)
    set_style_window_rounding(7.00)
    set_style_child_rounding(0.00)
    set_style_frame_rounding(2.30)
    set_style_popup_rounding(0.00)
    set_style_scrollbar_rounding(0.00)
    set_style_grab_rounding(0.00)
    set_style_tab_rounding(4.00)
    set_style_window_title_align(0.00, 0.50)
    set_style_window_menu_button_position(mvDir_Left)
    set_style_color_button_position(mvDir_Right)
    set_style_button_text_align(0.50, 0.50)
    set_style_selectable_text_align(0.00, 0.00)
    set_style_display_safe_area_padding(3.00, 3.00)
    set_style_global_alpha(1.00)
    set_style_antialiased_lines(True)
    set_style_antialiased_fill(True)
    set_style_curve_tessellation_tolerance(1.25)
    set_style_circle_segment_max_error(1.60)

    add_additional_font(os.path.join(heron_path, 'resources', 'fonts', 'SF-Pro-Rounded-Regular.ttf'), 18)
