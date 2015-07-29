'''
Created on Feb 27, 2015

@author: rgroten
'''
from functools import wraps  # for flask Auth

from flask import request, Response  # for flask Auth
from flask.globals import g
import ldap  # for LDAP

import NaFunctions


# from ldapurl import LDAP_SCOPE_SUBTREE  # for LDAP
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    isDebug = NaFunctions.getConfigOption("Debug")
    server = NaFunctions.getConfigOption("LdapServer")
    base_dn = NaFunctions.getConfigOption("BaseUserDn")
    bind_user="uid=" + username + "," + base_dn
    tls_cacert_file = NaFunctions.getConfigOption("TLSCACertFile")

    if tls_cacert_file:
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, tls_cacert_file)

    if isDebug == True:
        ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)

#     search_filter = "(&(objectClass=person)(uid=" + username + ")(member=cn=dba,cn=groups,cn=accounts," + base_dn + "))"
#     print "Filter is: " + search_filter
    connect = ldap.initialize(server)
    try:
        connect.bind_s(bind_user, password)
#         connect.search_s(base_dn, LDAP_SCOPE_SUBTREE, search_filter)
        connect.unbind_s()
        print("User %s successfully authenticated" % username)
        g.user = username
        g.env = "GENERAL"

        return True
    except Exception:
        connect.unbind_s()
        print("Authentication failed for %s" % username)
        return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Login required for this page\n'
    , 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})
    
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        isAuthReq = NaFunctions.getConfigOption("AuthRequired")
        if (isAuthReq == "False"):
            g.user = "NOUSER"
            return f(*args, **kwargs)
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
