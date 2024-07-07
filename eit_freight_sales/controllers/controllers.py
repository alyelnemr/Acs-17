import logging
from werkzeug.urls import url_encode
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import ensure_db

_logger = logging.getLogger(__name__)


class FreightController(AuthSignupHome):
    @http.route('/web/shipping-request', type='http', auth='public', website=True,
                sitemap=False)
    def web_shipping_request(self, *args, **kw):
        air_id = request.env['transport.type'].sudo().search([('code', '=', 'AIR')], limit=1).id
        sea_id = request.env['transport.type'].sudo().search([('code', '=', 'SEA')], limit=1).id
        inland_id = request.env['transport.type'].sudo().search([('code', '=', 'LND')], limit=1).id
        return request.render('eit_freight_request_quote.request_quote',
                              {
                                  'transport_type': request.env['transport.type'].sudo().search([]),
                                  'equipment_type_for_sea': request.env['shipment.scop'].sudo().search(
                                      [('type', '=', 'sea')]),
                                  'equipment_type_for_inland': request.env['shipment.scop'].sudo().search(
                                      [('type', '=', 'inland')]),
                                  'container_type': request.env['container.type'].sudo().search([]),
                                  'from_port_cities': request.env['port.cites'].sudo().search([('active', '=', True)],
                                                                                              limit=1),
                                  'to_port_cities': request.env['port.cites'].sudo().search([('active', '=', True)],
                                                                                            limit=1),
                                  'air_id': air_id,
                                  'sea_id': sea_id,
                                  'inland_id': inland_id,
                                  'commodity': request.env['commodity.data'].sudo().search([]),
                              })

    from odoo import http
    from odoo.http import request

    class ShippingRequestController(http.Controller):

        @http.route('/web/shipping-request', type='http', auth="public", methods=['POST'], website=True)
        def shipping_request(self, **kwargs):
            # Extract form data
            transport_type_id = kwargs.get('transport_type')
            dimensions_l = request.httprequest.form.getlist('dimensions_l[]')
            dimensions_w = request.httprequest.form.getlist('dimensions_w[]')
            dimensions_h = request.httprequest.form.getlist('dimensions_h[]')
            quantity = request.httprequest.form.getlist('quantity[]')
            weight = request.httprequest.form.getlist('weight[]')
            by_unit = True if kwargs.get('by_unit_checkbox') == 'on' else False
            by_unit_lcl = True if kwargs.get('by_unit_lcl_checkbox') == 'on' else False
            by_unit_ltl = True if kwargs.get('by_unit_ltl_checkbox') == 'on' else False
            weight_for_volume = request.httprequest.form.getlist('weight_for_volume[]')
            volume_for_volume = request.httprequest.form.getlist('volume_for_volume[]')
            weight_for_volume_fcl = request.httprequest.form.getlist('weight_for_volume_fcl[]')
            volume_for_volume_fcl = request.httprequest.form.getlist('volume_for_volume_fcl[]')
            weight_for_volume_ltl = request.httprequest.form.getlist('weight_for_volume_ltl[]')
            volume_for_volume_ltl = request.httprequest.form.getlist('volume_for_volume_ltl[]')
            weight_for_volume_lcl = request.httprequest.form.getlist('weight_for_volume_lcl[]')
            volume_for_volume_lcl = request.httprequest.form.getlist('volume_for_volume_lcl[]')
            equipment_type_for_sea = kwargs.get('equipment_type_for_sea')
            equipment_type_for_inland = kwargs.get('equipment_type_for_inland')
            container_type_id = request.httprequest.form.getlist('container_type[]')
            quantity_fcl = request.httprequest.form.getlist('quantity_fcl[]')
            weight_fcl = request.httprequest.form.getlist('weight_fcl[]')
            dimensions_l_lcl = request.httprequest.form.getlist('dimensions_l_lcl[]')
            dimensions_w_lcl = request.httprequest.form.getlist('dimensions_w_lcl[]')
            dimensions_h_lcl = request.httprequest.form.getlist('dimensions_h_lcl[]')
            quantity_lcl = request.httprequest.form.getlist('quantity_lcl[]')
            weight_lcl = request.httprequest.form.getlist('weight_lcl[]')
            dimensions_l_ltl = request.httprequest.form.getlist('dimensions_l_ltl[]')
            dimensions_w_ltl = request.httprequest.form.getlist('dimensions_w_ltl[]')
            dimensions_h_ltl = request.httprequest.form.getlist('dimensions_h_ltl[]')
            quantity_ltl = request.httprequest.form.getlist('quantity_ltl[]')
            weight_ltl = request.httprequest.form.getlist('weight_ltl[]')
            quantity_ftl = request.httprequest.form.getlist('quantity_ftl[]')
            weight_ftl = request.httprequest.form.getlist('weight_ftl[]')
            cbm_ltl = request.httprequest.form.getlist('cbm_ltl[]')
            cbm_lcl = request.httprequest.form.getlist('cbm_lcl[]')
            chw = request.httprequest.form.getlist('chw[]')
            from_port_cities_id = kwargs.get('from_port_cities')
            to_port_cities_id = kwargs.get('to_port_cities')
            commodity_id = kwargs.get('commodity')
            cargo_readiness_date = kwargs.get('cargo_readiness_date')
            additional_information = kwargs.get('additional_information')
            contact_name = kwargs.get('contact_name')
            contact_email = kwargs.get('contact_email')
            contact_company = kwargs.get('contact_company')
            country_code = kwargs.get('country_code')
            contact_phone = kwargs.get('contact_phone')

            # Create CRM Lead
            lead_vals = {
                'transport_type_id': int(transport_type_id),
                'additional_information': additional_information,
                'from_port_cities_id': int(from_port_cities_id),
                'to_port_cities_id': int(to_port_cities_id),
                'commodity_id': int(commodity_id),
                'cargo_readiness_date': cargo_readiness_date,
                'name': contact_name,
                'email_from': contact_email,
                'partner_name': contact_company,
                'phone': f"{country_code} {contact_phone}",
            }
            shipping_info_vals = []

            transport_type = request.env['transport.type'].sudo().browse(int(transport_type_id))
            if transport_type.code == 'LND':
                equipment_type = request.env['shipment.scop'].sudo().search([('code', '=', equipment_type_for_inland)], limit=1)
                lead_vals['equipment_type_id'] = equipment_type.id
                if equipment_type.code == 'FTL':
                    for i in range(len(container_type_id)):
                        shipping_info_vals.append({
                            'container_type_id': int(container_type_id[i]),
                            'quantity': int(quantity_ftl[i]) if quantity_ftl[i] else 0.0,
                            'weight': float(weight_ftl[i]) if weight_ftl[i] else 0.0,
                        })
                elif equipment_type.code == 'LTL':
                    lead_vals['by_unit'] = by_unit_ltl
                    if by_unit_ltl:
                        for i in range(len(dimensions_l_ltl)):
                            shipping_info_vals.append({
                                'dimensions_l': float(dimensions_l_ltl[i]) if dimensions_l_ltl[i] else 0.0,
                                'dimensions_w': float(dimensions_w_ltl[i]) if dimensions_w_ltl[i] else 0.0,
                                'dimensions_h': float(dimensions_h_ltl[i]) if dimensions_h_ltl[i] else 0.0,
                                'quantity': int(quantity_ltl[i]) if quantity_ltl[i] else 0.0,
                                'weight': float(weight_ltl[i]) if weight_ltl[i] else 0.0,
                                'cbm': float(cbm_ltl[i]) if cbm_ltl[i] else 0.0,
                            })
                    else:
                        for i in range(len(weight_for_volume_ltl)):
                            shipping_info_vals.append({
                                'weight': float(weight_for_volume_ltl[i]) if weight_for_volume_ltl[i] else 0.0,
                                'volume': float(volume_for_volume_ltl[i]) if volume_for_volume_ltl[i] else 0.0,
                            })
            elif transport_type.code == 'SEA':
                equipment_type = request.env['shipment.scop'].sudo().search([('code', '=', equipment_type_for_sea)], limit=1)
                lead_vals['equipment_type_id'] = equipment_type.id
                if equipment_type.code == 'FCL':
                    for i in range(len(container_type_id)):
                        shipping_info_vals.append({
                            'container_type_id': int(container_type_id[i]),
                            'quantity': int(quantity_ftl[i]) if quantity_ftl[i] else 0.0,
                            'weight': float(weight_ftl[i]) if weight_ftl[i] else 0.0,
                        })
                elif equipment_type.code == 'LCL':
                    lead_vals['by_unit'] = by_unit_lcl
                    if by_unit_lcl:
                        for i in range(len(dimensions_l_lcl)):
                            shipping_info_vals.append({
                                'dimensions_l': float(dimensions_l_lcl[i]) if dimensions_l_lcl[i] else 0.0,
                                'dimensions_w': float(dimensions_w_lcl[i]) if dimensions_w_lcl[i] else 0.0,
                                'dimensions_h': float(dimensions_h_lcl[i]) if dimensions_h_lcl[i] else 0.0,
                                'quantity': int(quantity_lcl[i]) if quantity_lcl[i] else 0.0,
                                'weight': float(weight_lcl[i]) if weight_lcl[i] else 0.0,
                                'cbm': float(cbm_lcl[i]) if cbm_lcl[i] else 0.0,
                            })
                    else:
                        for i in range(len(weight_for_volume_lcl)):
                            shipping_info_vals.append({
                                'weight': float(weight_for_volume_lcl[i]) if weight_for_volume_lcl[i] else 0.0,
                                'volume': float(volume_for_volume_lcl[i]) if volume_for_volume_lcl[i] else 0.0,
                            })
            elif transport_type.code == 'AIR':
                lead_vals['by_unit'] = by_unit
                if by_unit:
                    for i in range(len(dimensions_l)):
                        shipping_info_vals.append({
                            'dimensions_l': float(dimensions_l[i]) if dimensions_l[i] else 0.0,
                            'dimensions_w': float(dimensions_w[i]) if dimensions_w[i] else 0.0,
                            'dimensions_h': float(dimensions_h[i]) if dimensions_h[i] else 0.0,
                            'quantity': int(quantity[i]) if quantity[i] else 0.0,
                            'weight': float(weight[i]) if weight[i] else 0.0,
                            'chw': float(chw[i]) if chw[i] else 0.0,
                        })
                else:
                    for i in range(len(weight_for_volume)):
                        shipping_info_vals.append({
                            'weight': float(weight_for_volume[i]) if weight_for_volume[i] else 0.0,
                            'volume': float(volume_for_volume[i]) if volume_for_volume[i] else 0.0,
                        })

            # Create a new CRM opportunity record and link the shipping info
            # Search for an existing partner or create a new one
            partner = request.env['res.partner'].sudo().search([('email', '=', contact_email)], limit=1)
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name': contact_name,
                    'email': contact_email,
                    'company_name': contact_company,
                    'phone': f'{country_code} {contact_phone}'
                })
            lead_vals['partner_id'] = partner.id
            crm_lead = request.env['crm.lead'].sudo().create(lead_vals)

            for item in shipping_info_vals:
                item['crm_lead_id'] = crm_lead.id

            shipping_info = request.env['shipping.info'].sudo().create(shipping_info_vals)

            return request.redirect('/thank-you')

    @http.route('/thank-you', type='http', auth='public', website=True, sitemap=False)
    def thank_you(self, *args, **kw):
        return request.render('eit_freight_request_quote.thank_you_page')

    def _prepare_signup_values(self, qcontext):
        """Updated the values with newly added fields"""
        keys = ['login', 'name', 'password']
        configuration = request.env['signup.configuration'] \
            .sudo().search([], limit=1)
        for field in configuration.signup_field_ids:
            keys.append(field.field_id.name)
        values = {key: qcontext.get(key) for key in keys}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in
                                request.env['res.lang'].sudo().get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        return values

    @http.route('/web/signup', type='http', auth="public", website=True,
                sitemap=False)
    def website_signup(self):
        """Perform website signup."""
        values = {}
        configuration_signup = request.env[
            'configuration.signup'].sudo().search([], limit=1)
        if configuration_signup.is_show_terms_conditions:
            values[
                'terms_and_conditions'] = configuration_signup \
                .terms_and_conditions
        return request.render(
            "advance_signup_portal.advance_signup_portal.fields", values)
