import pyCore.resources as r
import os


def create_resources(apppath, config):
    r.add_library('stock', os.path.join(apppath, 'jsandcss'), config)

    # ----------------------------Basic CSS-----------------------
    r.add_css_resource('stock', 'bootstrap', 'css/bootstrap.min.css')
    r.add_css_resource('stock', 'font-5', 'font-awesome/css/all.css')
    r.add_css_resource('stock', 'font-awesome', 'font-awesome/css/v4-shims.css')
    r.add_css_resource('stock', 'sweetalert', 'css/plugins/sweetalert/sweetalert.css')
    r.add_css_resource('stock', 'animate', 'css/animate.css')
    r.add_css_resource('stock', 'style', 'css/style.css')
    r.add_css_resource('stock', 'rtl', 'css/plugins/bootstrap-rtl/bootstrap-rtl.min.css', 'bootstrap')

    # ----------------------------Basic JS----------------------------------------------------
    r.add_js_resource('stock', 'jquery', 'js/jquery-3.1.1.min.js')
    r.add_js_resource('stock', 'popper', 'js/popper.min.js')
    r.add_js_resource('stock', 'bootstrap', 'js/bootstrap.min.js')
    r.add_js_resource('stock', 'metismenu', 'js/plugins/metisMenu/jquery.metisMenu.js')
    r.add_js_resource('stock', 'slimscroll', 'js/plugins/slimscroll/jquery.slimscroll.min.js')
    r.add_js_resource('stock', 'pace', 'js/plugins/pace/pace.min.js')
    r.add_js_resource('stock', 'wow', 'js/plugins/wow/wow.min.js')
    r.add_js_resource('stock', 'sweetalert', 'js/plugins/sweetalert/sweetalert.min.js', 'pace')
    r.add_js_resource('stock', 'inspinia', 'js/inspinia.js', None)
