"""
    Demo of the widget

    I haven't gotten these views working with tests.
"""
from five import grok

from zope.interface import Interface, implements
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from zope.schema import getFieldsInOrder

from z3c.form import field
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE, IDataConverter
from z3c.form.converter import BaseDataConverter

from plone.directives import form

from collective.z3cform.datagridfield import DataGridFieldFactory, IDataGridField


class IAddress(Interface):
    address_type = schema.Choice(
        title = u'Address Type', required=True,
        values=[u'Work', u'Home'])
    line1 = schema.TextLine(
        title = u'Line 1', required=True)
    line2 = schema.TextLine(
        title = u'Line 2', required=False)
    city = schema.TextLine(
        title = u'City / Town', required=True)
    country = schema.TextLine(
        title = u'Country', required=True)

class AddressListField(schema.List):
    """We need to have a unique class for the field list so that we
    can apply a custom adapter."""
    pass

class IPerson(Interface):
    name = schema.TextLine(title=u'Name', required=True)
    address = AddressListField(title=u'Addresses',
        value_type=schema.Object(title=u'Address', schema=IAddress),
        required=True)

class Address(object):
    implements(IAddress)
    address_type = FieldProperty(IAddress['address_type'])
    line1 = FieldProperty(IAddress['line1'])
    line2 = FieldProperty(IAddress['line2'])
    city = FieldProperty(IAddress['city'])
    country = FieldProperty(IAddress['country'])

    def __init__(self, address_type=None, line1=None, line2=None, city=None, country=None):
        self.address_type = address_type
        self.line1 = line1
        self.line2 = line2
        self.city = city
        self.country = country

class AddressList(list):
    pass

class Person(object):
    implements(IPerson)
    name = FieldProperty(IPerson['name'])
    address = FieldProperty(IPerson['address'])

    def __init__(self, name=None, address=None):
        self.name = name
        self.address = address

class EditForm(form.EditForm):
    label = u'This is a simple, default layout - using Objects'

    grok.context(Interface)
    grok.name('demo-collective.z3cform.datagrid-object')

    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def getContent(self):
        return Person(
                name = u'MY NAME',
                address = AddressList([
                    Address(address_type = u'Work',
                        line1 = u'My Office',
                        line2 = u'Big Office Block',
                        city = u'Mega City',
                        country = u'The Old Sod'),
                    Address(address_type = u'Home',
                        line1 = u'Home Sweet Home',
                        line2 = u'Easy Street',
                        city = u'Burbs',
                        country = u'The Old Sod')
                ]))

class GridDataConverter(grok.MultiAdapter, BaseDataConverter):
    """Convert between the AddressList object and the widget"""
    
    grok.adapts(AddressListField, IDataGridField)
    grok.implements(IDataConverter)

    def toWidgetValue(self, value):
        """Simply pass the data through with no change"""
        rv = list()
        for row in value:
            d = dict()
            for name, field in getFieldsInOrder(IAddress):
                d[name] = getattr(row, name)
            rv.append(d)

        return rv

    def toFieldValue(self, value):
        rv = AddressList()
        for row in value:
            d = dict()
            for name, field in getFieldsInOrder(IAddress):
                d[name] = row[name]
            rv.append(Address(**d))
        return rv


class EditForm2(EditForm):
    label = u'This form has the insert and delete row options removed - using Objects'

    grok.name('demo-collective.z3cform.datagrid-object-no-manipulators')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm2, self).updateWidgets()
        self.widgets['address'].allow_insert = False
        self.widgets['address'].allow_delete = False

class EditForm3(EditForm):
    label = u'This form has the auto-append row options removed - using Objects'

    grok.name('demo-collective.z3cform.datagrid-object-no-auto-append')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def updateWidgets(self):
        super(EditForm3, self).updateWidgets()
        self.widgets['address'].auto_append = False

#### THIS ONE ONE NOT WORKING
#### Widgets already initialised when this code is called

class EditForm4(EditForm):
    label = u'This form has the country column removed - NOT WORKING - using Objects'

    grok.name('demo-collective.z3cform.datagrid-object-no-country')
    fields = field.Fields(IPerson)
    fields['address'].widgetFactory = DataGridFieldFactory

    def datagridInitialise(self, subform, widget):
        subform.fields = subform.fields.omit('country')

class EditForm5(EditForm):
    label = u'This form has column widths configured - using Objects'

    grok.name('demo-collective.z3cform.datagrid-object-column-widths')

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widgets['line1'].size = 40
        widgets['line2'].size = 40
        widgets['city'].size = 20
        widgets['country'].size = 10


class EditForm6(EditForm):
    label = u'This form has hidden the city column - using Objects'

    grok.name('demo-collective.z3cform.datagrid-object-hidden-column')

    def datagridUpdateWidgets(self, subform, widgets, widget):
        # This one hides the widgets
        widgets['city'].mode = HIDDEN_MODE

    def updateWidgets(self):
        # This one hides the column title
        super(EditForm6, self).updateWidgets()
        self.widgets['address'].columns[3]['mode']  = HIDDEN_MODE

class EditForm7(EditForm):
    label = u'This form shows a read-only table - using Objects'

    grok.name('demo-collective.z3cform.datagrid-object-read-only')

    def updateWidgets(self):
        super(EditForm7, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE

class EditForm8(EditForm):
    label = u'Table is readonly and cells are also readonly - using Objects'

    grok.name('demo-collective.z3cform.datagrid-object-read-only2')

    def updateWidgets(self):
        super(EditForm8, self).updateWidgets()
        self.widgets['address'].mode = DISPLAY_MODE
        for row in self.widgets['address'].widgets:
            for widget in row.subform.widgets.values():
                widget.mode = DISPLAY_MODE

