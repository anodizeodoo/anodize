from odoo import fields, models,_
from odoo.exceptions import ValidationError
from odoo.tools import  html2plaintext, is_html_empty


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    active_rule_sh = fields.Boolean('Active for Scholarship', default=False)

    scholarship_registration_id = fields.Many2one(
        'hr.employee.relative',
        string='Scholarship',
    )

    def _get_payslip_lines(self):
        res = super(HrPayslip,self)._get_payslip_lines()
        if not self.active_rule_sh:
            return res
        
        line_vals = []
        localdict = self.env.context.get('force_payslip_localdict', None)
        for payslip in self:
            if not payslip.scholarship_registration_id:
                continue

            if not payslip.contract_id:
                raise ValidationError(_("There's no contract set on payslip %s for %s."
                " Check that there is at least a contract set on the employee form.", payslip.name, payslip.employee_id.name))

            if localdict is None:
                localdict = payslip._get_localdict()

            rules_dict = localdict['rules'].dict
            result_rules_dict = localdict['result_rules'].dict

            blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

            result = {}
            for rule in sorted(payslip.scholarship_registration_id.scholarship_grade_id.salary_rule, key=lambda x: x.sequence):
                if rule.id in blacklisted_rule_ids:
                    continue

                localdict.update({
                    'result': None,
                    'result_qty': 1.0,
                    'result_rate': 100,
                    'result_name': False
                })

                if rule._satisfy_condition(localdict):
                    # Retrieve the line name in the employee's lang
                    employee_lang = payslip.employee_id.sudo().address_home_id.lang
                    # This actually has an impact, don't remove this line
                    if rule.code in localdict['same_type_input_lines']:
                        for multi_line_rule in localdict['same_type_input_lines'][rule.code]:
                            localdict['inputs'].dict[rule.code] = multi_line_rule
                            amount, qty, rate = rule._compute_rule(localdict)
                            tot_rule = amount * qty * rate / 100.0
                            localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule)
                            rule_name = payslip._get_rule_name(localdict, rule, employee_lang)
                            
                            line_vals.append({
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name':  rule_name,
                                'note': html2plaintext(rule.note) if not is_html_empty(rule.note) else '',
                                'salary_rule_id': rule.id,
                                'contract_id': localdict['contract'].id,
                                'employee_id': localdict['employee'].id,
                                'amount': amount,
                                'quantity': qty,
                                'rate': rate,
                                'slip_id': payslip.id,
                            })
                    else:
                        amount, qty, rate = rule._compute_rule(localdict)
                        #check if there is already a rule computed with that code
                        previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                        #set/overwrite the amount computed for this rule in the localdict
                        tot_rule = amount * qty * rate / 100.0
                        localdict[rule.code] = tot_rule
                        result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                        rules_dict[rule.code] = rule
                        # sum the amount for its salary category
                        localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                        rule_name = payslip._get_rule_name(localdict, rule, employee_lang)
                        # create/overwrite the rule in the temporary results
                        result[rule.code] = {
                            'sequence': rule.sequence,
                            'code': rule.code,
                            'name': rule_name,
                            'note': html2plaintext(rule.note) if not is_html_empty(rule.note) else '',
                            'salary_rule_id': rule.id,
                            'contract_id': localdict['contract'].id,
                            'employee_id': localdict['employee'].id,
                            'amount': amount,
                            'quantity': qty,
                            'rate': rate,
                            'slip_id': payslip.id,
                        }
            line_vals += list(result.values())
        return line_vals
