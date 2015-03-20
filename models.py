from openerp import models, fields, api, exceptions, _
import xlrd
import base64


class sale_order(models.Model):
    _inherit = 'sale.order'

    xls_data = fields.Binary()

    @api.one
    def import_from_xls(self):
        if self.xls_data:
            xls = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_data))
            sheet = xls.sheet_by_index(0)
            correct_lines =[]
            for row in range(1, sheet.nrows):
                default_code = sheet.cell(row, 1).value
                if default_code:
                    if isinstance(default_code, int) or isinstance(default_code, float):
                        default_code = '%d' % default_code
                    products = self.env["product.product"].search([('default_code', '=', default_code)])
                    if len(products) > 0:
                        product_id = products[0].id
                    else:
                        raise exceptions.UserError('error in line:%d.default code:%s not exist!' % (row, default_code))
                else:
                    break

                qty = sheet.cell(row, 3).value
                if not qty or qty <= 0:
                    raise exceptions.UserError('error in line:%d.Quantity must greater then zero!' % row)

                price = sheet.cell(row, 4).value
                if not price:
                    raise exceptions.UserError('error in line:%d.Price must greater then zero!' % row)

                correct_lines.append((product_id, qty, price))

            for line in correct_lines:
                self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': line[0],
                    'product_uom_qty': line[1],
                    'price_unit': line[2],
                })
        else:
            raise exceptions.UserError('Upload Excel files first!')