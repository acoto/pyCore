"""
This file declares the PCA interfaces available in Stock Exchange and their methods.
"""


__all__ = [
    'Interface',
    'IRoutes',
    'IConfig',
    'IResource',
    'IPluginObserver',
    'IPluralize',
    'ISchema',
    'IDatabase',
    'IAuthorize',
    'ITemplateHelpers'
]


from inspect import isclass
from pyutilib.component.core import Interface as _pca_Interface


class Interface(_pca_Interface):
    """
        This code is based on CKAN
        :Copyright (C) 2007 Open Knowledge Foundation
        :license: AGPL V3, see LICENSE for more details.

     """
    @classmethod
    def provided_by(cls, instance):
        return cls.implemented_by(instance.__class__)

    @classmethod
    def implemented_by(cls, other):
        if not isclass(other):
            raise TypeError("Class expected", other)
        try:
            return cls in other._implements
        except AttributeError:
            return False


class IRoutes(Interface):
    """
    Plugin into the creation of routes.

    """
    def before_mapping(self, config):
        """
        Called before the mapping of routes made by Stock Exchange.

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'name':'myroute','path':'/myroute','view',viewDefinition,
                                       'renderer':'renderere_used'}]
        """
        raise NotImplementedError("before_mapping must be implemented in subclasses")

    def after_mapping(self, config):
        """
        Called after the mapping of routes made by Stock Exchange.

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'name':'myroute','path':'/myroute','view',viewDefinition,
                                       'renderer':'renderere_used'}]
        """
        raise NotImplementedError("after_mapping must be implemented in subclasses")


class IConfig(Interface):
    """
    Allows the modification of the Pyramid config. For example to add new templates or static directories
    """

    def update_config(self, config):
        """
        Called by Stock Exchange during the initialization of the environment

        :param config: ``pyramid.config`` object
        """


class IResource(Interface):
    """
        Allows to hook into the creation of JS and CSS libraries or resources
    """

    def add_libraries(self, config):
        """
        Called by Stock Exchange so plugins can add new JS and CSS libraries to Stock Exchange

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'name':'mylibrary','path':'/path/to/my/resources'}]
        """
        raise NotImplementedError("add_libraries must be implemented in subclasses")

    def add_js_resources(self, config):
        """
        Called by Stock Exchange so plugins can add new JS Resources
        
        :param config: ``pyramid.config`` object        
        :return Returns a dict array [{'libraryname':'mylibrary','id':'myResourceID','file':'/relative/path/to/jsFile',
                                      'depends':'resourceID'}]
        """
        raise NotImplementedError("add_js_resources must be implemented in subclasses")

    def add_css_resources(self, config):
        """
        Called by Stock Exchange so plugins can add new FanStatic CSS Resources

        :param config: ``pyramid.config`` object        
        :return Returns a dict array [{'libraryname':'mylibrary','id':'myResourceID','file':'/relative/path/to/jsFile',
                                      'depends':'resourceID'}]
        """
        raise NotImplementedError("add_css_resources must be implemented in subclasses")


class IPluralize(Interface):
    """
        Allows to hook into the pluralization function so plugins can extend the pluralization of Stock Exchange
    """
    def pluralize(self, noun, locale):
        """
            Called the packages are created

            :param noun: ``Noun to be pluralized``
            :param locale: ``The current locate code e.g. en``
            :return the noun in plural form
        """


class ISchema(Interface):
    """
        Allows to hook into the schema layer and add new fields into it.
        The schema is a layer on top of the database schema so plugin developers can
        add new fields to Stock Exchange tables without affecting the structure
        of the database. New fields are stored in extra as JSON keys
    """

    def update_schema(self, config):
        """
        Called by the host application so plugins can add new fields to table schemata

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'schema':'schema_to_update','fieldname':'myfield',
                                       'fielddesc':'A good description of myfield'}]

        Plugin writers should use the utility functions:
            - addFieldToUserSchema
            - addFieldToProjectSchema
            - addFieldToEnumeratorSchema
            - addFieldToEnumeratorGroupSchema
            - addFieldToDataUserSchema
            - addFieldToDataGroupSchema
            - addFieldToFormSchema


        Instead of constructing the dict by themselves to ensure API compatibility

        """
        raise NotImplementedError("update_schema must be implemented in subclasses")


class IDatabase(Interface):
    """
        Allows to hook into the database schema so plugins can add new tables
        After calling this
    """

    def update_orm(self, metadata):
        """
        Called by Stock Exchange so plugins can add new tables to Stock Exchange ORM

        :param metadata: Stock Exchange ORM metadata object

        """


class IAuthorize(Interface):
    """
        Allows to hook into the user authorization
        After calling this
    """

    def after_login(self, request, user):
        """
        Called by the host application so plugins can modify the login of users

        :param request: ``pyramid.request`` object
        :param user: user object
        :return Return true or false if the login should continue. If False then a message should state why

        """
        raise NotImplementedError("after_login must be implemented in subclasses")

    def before_register(self, request, registrant):
        """
        Called by the host application so plugins can do something before registering a user

        :param request: ``pyramid.request`` object
        :param registrant: Dictionary containing the details of the registrant
        :return Return a modified version of registrant, true or false if the registrant should be added. If False then
        a message should state why

        """
        raise NotImplementedError("before_register must be implemented in subclasses")

    def after_register(self, request, registrant):
        """
        Called by the host application so plugins do something after registering a user

        :param request: ``pyramid.request`` object
        :param registrant: Dictionary containing the details of the registrant
        :return Return the next page that will be loaded after the registration. If empty or None the the Stock Exchange
        dashboard will be loaded

        """
        raise NotImplementedError("on_authenticate_user must be implemented in subclasses")

    def on_authenticate_user(self, request, user_id):
        """
                Called by Stock Exchange so plugins can modify the way Stock Exchange gather information about the user

                :param request: ``pyramid.request`` object
                :param user_id: The user ID trying to authenticate
                :return Return None and and empty Dict to indicate that Forshare should get this in the normal way.
                        False and None if the user must be denied.
                        Otherwise true and then the Dict MUST contain at least the following keys:
                        user_id : With the same userID authenticating
                        user_email : With the email of the userID authenticating
                        user_name : With the full name of the userID authenticating
                        user_about : With the bio data of the userID authenticating or None
                """
        raise NotImplementedError("on_authenticate_user must be implemented in subclasses")

    def on_authenticate_password(self, request, user_id, password):
        """
                Called by Stock Exchange so plugins can modify the way Stock Exchange gather information about the user

                :param request: ``pyramid.request`` object
                :param user_id: The user ID trying to authenticate
                :param password: The password as is typed in the Stock Exchange interface
                :return Return None to indicate that Forshare should get this in the normal way.
                        False if the password is incorrect.
                        Otherwise true
                        """
        raise NotImplementedError("on_authenticate_password must be implemented in subclasses")


class ITemplateHelpers(Interface):
    """
    Add custom template helper functions.

    By implementing this plugin interface plugins can provide their own
    template helper functions, which custom templates can then access via the
    ``request.h`` variable.
    """
    def get_helpers(self):
        """
        Return a dict mapping names to helper functions.

        The keys of the dict should be the names with which the helper
        functions will be made available to templates, and the values should be
        the functions themselves. For example, a dict like:
        ``{'example_helper': example_helper}`` allows templates to access the
        ``example_helper`` function via ``request.h.example_helper()``.

        Function names should start with the name of the extension providing
        the function, to prevent name clashes between extensions.
        :return:
        """


class IPluginObserver(Interface):
    """
    Plugin to the plugin loading mechanism

    This code is based on CKAN
    :Copyright (C) 2007 Open Knowledge Foundation
    :license: AGPL V3, see LICENSE for more details.

    """

    def before_load(self, plugin):
        """
        Called before a plugin is loaded
        This method is passed the plugin class.
        """

    def after_load(self, service):
        """
        Called after a plugin has been loaded.
        This method is passed the instantiated service object.
        """

    def before_unload(self, plugin):
        """
        Called before a plugin is loaded
        This method is passed the plugin class.
        """

    def after_unload(self, service):
        """
        Called after a plugin has been unloaded.
        This method is passed the instantiated service object.
        """
