from . import models

def post_init_hook(env):
    modules_to_uninstall = ['spreadsheet']

    for module_name in modules_to_uninstall:
        module = env['ir.module.module'].search([('name', '=', module_name)])
        if module and module.state == 'installed':
            module.button_uninstall()