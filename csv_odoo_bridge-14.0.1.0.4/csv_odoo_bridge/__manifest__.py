# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "CSV Connector",
  "summary"              :  """Import Orders From CSV extension provides csv import options receive from multiple ecommerce marketplaces.admin can import order csv as well product csv and partner csv in odoo.""",
  "category"             :  "Website",
  "version"              :  "1.0.4",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Import-Orders-From-CSV.html",
  "description"          :  """Import Orders From CSV is the  Odoo Extension provides csv import options receive from multiple marketplace and eCommerce Platform. It manage the mapping of order, product, partner for avoiding the duplicity, it's work in support with Odoo Multi-Channel Sale. Using this module when admin import order csv in odoo, it create the product and partner automatically from a singe order csv on the basis of mapped fields and set the order (create invoice open/paid, Create Delivery/Stock Picking) on basis of order state mapping.""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=csv_odoo_bridge&version=13.0",
  "depends"              :  ['odoo_multi_channel_sale'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/data.xml',
                             'views/dashboard.xml',
                             'views/views.xml',
                             'views/search.xml',
                             'wizard/wizard.xml',
                            ],
  "qweb"                 :  ['static/src/xml/instance_dashboard.xml'],
  "images"               :  ['static/description/banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  10.0,
  "currency"             :  "USD",
}
