import itertools

from odoo import api, fields, models, _, Command
from collections import defaultdict
from odoo.exceptions import UserError, ValidationError, RedirectWarning

class AccountAccount(models.Model):
  _inherit = "account.account"

  @api.model
  def _search_new_account_name(self, start_name, cache=None):
      """Get an account name that is available for creating a new account in the active company
      by starting from an existing name and appending `.copy`, `.copy2`, ... if needed.

      Similar to `_search_new_account_code`, but for `name` field.
      """

      if cache is None:
          cache = {start_name}

      def name_is_available(new_name):
          """Check if name is not already used within parent/child companies."""
          return (
              new_name not in cache
              and not self.sudo().search_count([
                  ('name', '=', new_name),
                  '|',
                  ('company_ids', 'parent_of', self.env.company.id),
                  ('company_ids', 'child_of', self.env.company.id),
              ], limit=1)
          )

      if name_is_available(start_name):
          return start_name

      # Try fallback names like: name.copy, name.copy2, ..., name.copy99
      for num in range(99):
          new_name = f'{start_name}.copy{num + 1 if num else ""}'
          if name_is_available(new_name):
              return new_name

      raise UserError(_('Cannot generate an unused account name.'))
  
  @api.model_create_multi
  def create(self, vals_list):
        records_list = []

        for company_ids, vals_list_for_company in itertools.groupby(vals_list, lambda v: v.get('company_ids', [])):
            cache = set()
            vals_list_for_company = list(vals_list_for_company)

            # Determine the companies the new accounts will have.
            company_ids = self._fields['company_ids'].convert_to_cache(company_ids, self.browse())
            companies = self.env['res.company'].browse(company_ids)
            if self.env.company in companies or not companies:
                companies = self.env.company | companies  # The currently active company comes first.

            for vals in vals_list_for_company:
                if 'prefix' in vals:
                    prefix, digits = vals.pop('prefix'), vals.pop('code_digits')
                    start_code = prefix.ljust(digits - 1, '0') + '1' if len(prefix) < digits else prefix
                    vals['code'] = self.with_company(companies[0])._search_new_account_code(start_code, cache)
                    cache.add(vals['code'])

                if 'code' not in vals:  # prepopulate the code for precomputed fields depending on it
                    for mapping_command in vals.get('code_mapping_ids', []):
                        match mapping_command:
                            case Command.CREATE, _, {'company_id': company_id, 'code': code} if company_id == companies[0].id:
                                vals['code'] = code
                                break

            new_accounts = super(AccountAccount, self.with_context(
                allowed_company_ids=companies.ids,
                defer_account_code_checks=True,
                # Don't get a default value for `code_mapping_ids` from default_get
                default_code_mapping_ids=self.env.context.get('default_code_mapping_ids', []),
            )).create(vals_list_for_company)

            records_list.append(new_accounts)

        records = self.env['account.account'].union(*records_list)
        records._ensure_code_is_unique()
        records._ensure_name_is_unique()
        return records
  
  def write(self, vals):
        if 'reconcile' in vals:
            if vals['reconcile']:
                self.filtered(lambda r: not r.reconcile)._toggle_reconcile_to_true()
            else:
                self.filtered(lambda r: r.reconcile)._toggle_reconcile_to_false()

        if vals.get('currency_id'):
            for account in self:
                if self.env['account.move.line'].search_count([('account_id', '=', account.id), ('currency_id', 'not in', (False, vals['currency_id']))]):
                    raise UserError(_('You cannot set a currency on this account as it already has some journal entries having a different foreign currency.'))

        res = super(AccountAccount, self.with_context(defer_account_code_checks=True)).write(vals)

        if not self.env.context.get('defer_account_code_checks') and {'company_ids', 'code', 'code_mapping_ids'} & vals.keys():
            self._ensure_code_is_unique()
        
        if not self.env.context.get('defer_account_code_checks') and {'company_ids', 'name'} & vals.keys():
            self._ensure_name_is_unique()

        return res

  def _ensure_name_is_unique(self):
    """ Check account names per companies. These are the checks:

        1. Check that the name is set for each of the account's companies.

        2. Check that no child or parent companies have another account with the same name
           as the account.
    """
    # Check 1: Check that the name is set.
    for account in self.sudo():
        for company in account.company_ids.root_id:
            if not account.with_company(company).name:
                raise ValidationError(_("The name must be set for every company to which this account belongs."))

    # Check 2: Check that no child or parent companies have an account with the same name.
    account_ids_to_check_by_company = defaultdict(list)
    for account in self.sudo():
        companies_to_check = account.company_ids
        for company in companies_to_check:
            account_ids_to_check_by_company[company].append(account.id)

    for company, account_ids in account_ids_to_check_by_company.items():
        accounts = self.browse(account_ids).with_prefetch(self.ids).sudo()

        # Check 2.1: Check that there are no duplicates in the given recordset.
        accounts_by_name = defaultdict(list)
        for acc in accounts.with_company(company):
            accounts_by_name[acc.name].append(acc)

        duplicate_names = None
        if any(len(accs) > 1 for accs in accounts_by_name.values()):
            duplicate_names = [name for name, accs in accounts_by_name.items() if len(accs) > 1]

        # Check 2.2: Check that there are no duplicates in the database
        elif duplicates := self.with_company(company).sudo().search_fetch(
            [
                ('name', 'in', list(accounts_by_name)),
                ('id', 'not in', self.ids),
                '|',
                ('company_ids', 'parent_of', company.ids),
                ('company_ids', 'child_of', company.ids),
            ],
            ['name'],
        ):
            duplicate_names = duplicates.mapped('name')

        if duplicate_names:
            raise ValidationError(
                _("Account names must be unique. You can't create accounts with these duplicate names: %s") % ", ".join(duplicate_names)
            )
