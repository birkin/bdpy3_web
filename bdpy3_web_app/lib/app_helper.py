# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, time
import requests
from bdpy3 import BorrowDirect
from bdpy3_web_app import settings_app


log = logging.getLogger(__name__)


class Validator( object ):
    """ Contains validation functions for views.v1() """

    def __init__( self ):
        log.debug( 'helper initialized' )
        pass

    def validate_request( self, method, ip, post_params ):
        """ Checks request validity; returns boolean.
            Called by bdpyweb_app.handle_v1() """
        log.debug( 'method, `%s`' % method )
        validity = False
        if method == 'GET':  # for dev; will be POST
            if self.check_keys( post_params ) is True:
                if self.check_ip( ip ) is True:
                    if self.check_auth( post_params ) is True:
                        validity = True
        log.debug( 'overall_validity, `%s`' % validity )
        return validity

    def check_keys( self, params ):
        """ Checks required keys; returns boolean.
            Called by validate_request() """
        log.debug( 'params, ```%s```' % pprint.pformat(params) )
        keys_good = False
        required_keys = [ 'api_authorization_code', 'api_identity', 'isbn',  'user_barcode' ]
        for required_key in required_keys:
            if required_key not in params.keys():
                break
            if required_key == required_keys[-1]:
                keys_good = True
        log.debug( 'keys_good, `%s`' % keys_good )
        return keys_good

    def check_ip( self, ip ):
        """ Checks ip; returns boolean.
            Called by validate_request() """
        validity = False
        if ip in settings_app.LEGIT_IPS:
            validity = True
        else:
            log.debug( 'bad ip, `%s`' % ip )
        log.debug( 'validity, `%s`' % validity )
        return validity

    def check_auth( self, params ):
        """ Checks auth params; returns boolean.
            Called by validate_request() """
        validity = False
        if params.get( 'api_authorization_code', 'nope' ) == settings_app.WEB_API_AUTHORIZATION_CODE:
            if params.get( 'api_identity', 'nope' ) == settings_app.WEB_API_IDENTITY:
                validity = True
        log.debug( 'validity, `%s`' % validity )
        return validity

    ## end class Validator()



class LibCaller( object ):
    """ Contains functions for bdpy3 call. """

    def __init__( self ):
        self.defaults = {
            'API_URL_ROOT': settings_app.BDPY3_API_URL_ROOT,
            'API_KEY': settings_app.BDPY3_API_KEY,
            'UNIVERSITY_CODE': settings_app.BDPY3_UNIVERSITY_CODE,
            'PARTNERSHIP_ID': settings_app.BDPY3_PARTNERSHIP_ID,
            'PICKUP_LOCATION': settings_app.BDPY3_PICKUP_LOCATION,
            }

    def do_lookup( self, params ):
        """ Runs lookup; returns bdpy3 output.
            Called by bdpyweb_app.handle_v1() """
        log.debug( 'params, ```%s```' % pprint.pformat(params) )
        log.debug( 'self.defaults, ```%s```' % pprint.pformat(self.defaults) )
        bd = BorrowDirect( self.defaults )
        # bd.run_request_item( params['user_barcode'], 'ISBN', params['isbn'] )
        # self.logger.debug( 'bd.request_result, `%s`' % bd.request_result )
        # return bd.request_result
        bd.run_search( params['user_barcode'], 'ISBN', params['isbn'] )
        log.debug( 'bd.search_result, `%s`' % bd.search_result )
        return bd.search_result

    def interpret_result( self, bdpy_result ):
        """ Examines api result and prepares response expected by easyborrow controller.
            Called by bdpyweb_app.handle_v1()
            Note: at the moment, it does not appear that the new BD api distinguishes between 'found' and 'requestable'. """
        return_dct = {
            'search_result': 'FAILURE', 'bd_confirmation_code': None, 'found': False, 'requestable': False }
        if 'RequestNumber' in bdpy_result.keys():
            return_dct['search_result'] = 'SUCCESS'
            return_dct['bd_confirmation_code'] = bdpy_result['RequestNumber']
            return_dct['found'] = True
            return_dct['requestable'] = True
        self.logger.debug( 'interpreted result-dct, `%s`' % pprint.pformat(return_dct) )
        return return_dct

    def load_bdpy_defaults( self ):
        """ Loads up non-changing bdpy defaults.
            Called by do_lookup() """
        defaults = {
            'API_URL_ROOT': unicode( os.environ['bdpyweb__BDPY_API_ROOT_URL'] ),
            'API_KEY': unicode( os.environ['bdpyweb__BDPY_API_KEY'] ),
            'UNIVERSITY_CODE': unicode( os.environ['bdpyweb__BDPY_UNIVERSITY_CODE'] ),
            'PARTNERSHIP_ID': unicode( os.environ['bdpyweb__BDPY_PARTNERSHIP_ID'] ),
            'PICKUP_LOCATION': unicode( os.environ['bdpyweb__BDPY_PICKUP_LOCATION'] ),
            }
        self.logger.debug( 'defaults, `%s`' % defaults )
        return defaults

    ## end class LibCaller()


# class EzbHelper( object ):
#     """ Helper functions for views.v1() """

#     def __init__( self ):
#         log.debug( 'helper initialized' )
#         pass

#     def validate_request( self, method, ip, post_params ):
#         """ Checks request validity; returns boolean.
#             Called by bdpyweb_app.handle_v1() """
#         log.debug( 'method, `%s`' % method )
#         validity = False
#         if method == 'GET':  # for dev; will be POST
#             if self.check_keys( post_params ) is True:
#                 if self.check_ip( ip ) is True:
#                     if self.check_auth( post_params ) is True:
#                         validity = True
#         log.debug( 'overall_validity, `%s`' % validity )
#         return validity

#     def do_lookup( self, params ):
#         """ Runs lookup; returns bdpy output.
#             Called by bdpyweb_app.handle_v1() """
#         self.logger.debug( 'params, `%s`' % pprint.pformat(params) )
#         defaults = self.load_bdpy_defaults()
#         bd = BorrowDirect( defaults, self.logger )
#         bd.run_request_item( params['user_barcode'], 'ISBN', params['isbn'] )
#         self.logger.debug( 'bd.request_result, `%s`' % bd.request_result )
#         return bd.request_result

#     def interpret_result( self, bdpy_result ):
#         """ Examines api result and prepares response expected by easyborrow controller.
#             Called by bdpyweb_app.handle_v1()
#             Note: at the moment, it does not appear that the new BD api distinguishes between 'found' and 'requestable'. """
#         return_dct = {
#             'search_result': 'FAILURE', 'bd_confirmation_code': None, 'found': False, 'requestable': False }
#         if 'RequestNumber' in bdpy_result.keys():
#             return_dct['search_result'] = 'SUCCESS'
#             return_dct['bd_confirmation_code'] = bdpy_result['RequestNumber']
#             return_dct['found'] = True
#             return_dct['requestable'] = True
#         self.logger.debug( 'interpreted result-dct, `%s`' % pprint.pformat(return_dct) )
#         return return_dct

#     ## helper functions (called by above functions)

#     def load_bdpy_defaults( self ):
#         """ Loads up non-changing bdpy defaults.
#             Called by do_lookup() """
#         defaults = {
#             'API_URL_ROOT': unicode( os.environ['bdpyweb__BDPY_API_ROOT_URL'] ),
#             'API_KEY': unicode( os.environ['bdpyweb__BDPY_API_KEY'] ),
#             'UNIVERSITY_CODE': unicode( os.environ['bdpyweb__BDPY_UNIVERSITY_CODE'] ),
#             'PARTNERSHIP_ID': unicode( os.environ['bdpyweb__BDPY_PARTNERSHIP_ID'] ),
#             'PICKUP_LOCATION': unicode( os.environ['bdpyweb__BDPY_PICKUP_LOCATION'] ),
#             }
#         self.logger.debug( 'defaults, `%s`' % defaults )
#         return defaults

#     def check_keys( self, params ):
#         """ Checks required keys; returns boolean.
#             Called by validate_request() """
#         log.debug( 'params, ```%s```' % pprint.pformat(params) )
#         keys_good = False
#         required_keys = [ 'api_authorization_code', 'api_identity', 'isbn',  'user_barcode' ]
#         for required_key in required_keys:
#             if required_key not in params.keys():
#                 break
#             if required_key == required_keys[-1]:
#                 keys_good = True
#         log.debug( 'keys_good, `%s`' % keys_good )
#         return keys_good

#     def check_ip( self, ip ):
#         """ Checks ip; returns boolean.
#             Called by validate_request() """
#         validity = False
#         if ip in settings_app.LEGIT_IPS:
#             validity = True
#         else:
#             log.debug( 'bad ip, `%s`' % ip )
#         log.debug( 'validity, `%s`' % validity )
#         return validity

#     def check_auth( self, params ):
#         """ Checks auth params; returns boolean.
#             Called by validate_request() """
#         validity = False
#         if params.get( 'api_authorization_code', 'nope' ) == settings_app.API_AUTHORIZATION_CODE:
#             if params.get( 'api_identity', 'nope' ) == settings_app.API_IDENTITY:
#                 validity = True
#         log.debug( 'validity, `%s`' % validity )
#         return validity

#     # end class EzbHelper


class FormHelper( object ):
    """ Not currently in-use. """

    def __init__( self, logger ):
        """ Helper functions for app->handle_form() """
        self.logger = logger
        self.logger.debug( 'form_helper initialized' )
        self.defaults = {
            'UNIVERSITY_CODE': unicode( os.environ['bdpyweb__BDPYTEST_UNIVERSITY_CODE'] ),
            'API_URL_ROOT': unicode( os.environ['bdpyweb__BDPYTEST_API_ROOT_URL'] ),
            'PARTNERSHIP_ID': unicode( os.environ['bdpyweb__BDPYTEST_PARTNERSHIP_ID'] ),
            'PICKUP_LOCATION': unicode( os.environ['bdpyweb__BDPYTEST_PICKUP_LOCATION'] ),
            'PATRON_BARCODE': unicode( os.environ['bdpyweb__BDPYTEST_PATRON_BARCODE'] ),
            'AVAILABILITY_API_URL_ROOT': unicode( os.environ['bdpyweb__BDPYTEST_AVAILABILITY_API_URL_ROOT'] )
            }

    ## main functions

    def run_search( self, isbn ):
        """ Hits test-server with search & returns output.
            Called by bdpyweb_app.handle_form_post() """
        bd = BorrowDirect( self.defaults, self.logger )
        bd.run_search( self.defaults['PATRON_BARCODE'], 'ISBN', isbn )
        bdpy_result = bd.search_result
        if bdpy_result.get( 'Item', None ) and bdpy_result['Item'].get( 'AuthorizationId', None ):
            bdpy_result['Item']['AuthorizationId'] = '(hidden)'
        return bdpy_result

    def run_request( self, isbn ):
        """ Hits test-server with request & returns output.
            Called by bdpyweb_app.handle_form_post() """
        time.sleep( 1 )
        bd = BorrowDirect( self.defaults, self.logger )
        bd.run_request_item( self.defaults['PATRON_BARCODE'], 'ISBN', isbn )
        bdpy_result = bd.request_result
        return bdpy_result

    def hit_availability_api( self, isbn ):
        """ Hits hit_availability_api for holdings data.
            Called by bdpyweb_app.handle_form_post() """
        url = '%s/%s/' % ( self.defaults['AVAILABILITY_API_URL_ROOT'], isbn )
        r = requests.get( url )
        dct = r.json()
        items = dct['items']
        for item in items:
            for key in ['is_available', 'requestable', 'barcode', 'callnumber']:
                del item[key]
        return_dct = {
            'title': dct.get( 'title', None ),
            'items': items }
        return return_dct

    def build_response_jsn( self, isbn, search_result, request_result, availability_api_data, start_time ):
        """ Prepares response data.
            Called by bdpyweb_app.handle_form_post() """
        end_time = datetime.datetime.now()
        response_dct = {
            'request': { 'datetime': unicode(start_time), 'isbn': isbn },
            'response': {
                'availability_api_data': availability_api_data,
                'bd_api_testserver_search_result': search_result,
                'bd_api_testserver_request_result': request_result,
                'time_taken': unicode( end_time - start_time ) }
                }
        self.logger.debug( 'response_dct, `%s`' % pprint.pformat(response_dct) )
        return json.dumps( response_dct, sort_keys=True, indent=4 )

    # end class FormHelper
