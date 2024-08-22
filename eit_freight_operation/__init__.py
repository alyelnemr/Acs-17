from . import models
from . import controllers
from . import reports
from . import wizard


def _update_ir_module_category(env):
    # rename the project module name in user permission screen
    env.cr.execute("""
        UPDATE ir_module_category 
        SET name = '{"en_US": "Operations"}'
        WHERE name::text LIKE '%Project%';
    """)
