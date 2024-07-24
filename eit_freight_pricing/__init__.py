# -*- coding: utf-8 -*-

from . import controllers
from . import models
from . import wizard


def post_init_hook(env):
    modules_to_install = ['sale_product_matrix']

    for module_name in modules_to_install:
        module = env['ir.module.module'].search([('name', '=', module_name)])
        if module:
            # Check if the module is already installed
            if module.state != 'installed':
                # Force install the module
                module.button_install()
        else:
            print('nottttttttttttttttttttttttt')
