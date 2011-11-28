from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    ReferenceField('Product',
        required = 1,
        allowed_types = ('LabProduct',),
        relationship = 'SupplyOrderItemLabProduct',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = _("Product"),
        )
    ),
    IntegerField('Quantity',
        required = 1,
        default = '0',
        widget = IntegerWidget(
            label = _("Quantity"),
        )
    ),
    FixedPointField('Price',
        required = 1,
        widget = DecimalWidget(
            label = _("Unit price"),
        )
    ),
    FixedPointField('VAT',
        required = 1,
        widget = DecimalWidget(
            label = _("VAT"),
        ),
    ),
),
)

class SupplyOrderItem( BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def Title(self):
        """ Return the Product as title """
        product = self.getProduct()
        if product:
            return product.Title()
        else:
            return ''

    security.declareProtected(View, 'getTotal')
    def getTotal(self):
        """ compute total excluding VAT """
        price = self.getPrice()
        if price:
            return self.getPrice() * self.getQuantity()
        else:
            return 0

    security.declareProtected(View, 'getTotalIncludingVAT')
    def getTotalIncludingVAT(self):
        """ Compute Total including VAT """
        price = self.getPrice()
        quantity = self.getQuantity()
        vat = self.getVAT()
        if price and quantity and vat:
            subtotal = price * quantity
            return subtotal * (1 + vat / 100.0)
        else:
            return 0


atapi.registerType(SupplyOrderItem, PROJECTNAME)
