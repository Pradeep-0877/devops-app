from ldap3 import Server, Connection, ALL, NTLM
from ldap3.core.exceptions import LDAPException
from typing import Optional, Dict
from app.core.config import settings
from loguru import logger


class LDAPAuthenticator:
    """LDAP Authentication Service"""
    
    def __init__(self):
        self.server_uri = settings.LDAP_SERVER
        self.base_dn = settings.LDAP_BASE_DN
        self.user_dn = settings.LDAP_USER_DN
        self.bind_user = settings.LDAP_BIND_USER
        self.bind_password = settings.LDAP_BIND_PASSWORD
        self.search_filter = settings.LDAP_SEARCH_FILTER
        
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user against LDAP server
        
        Args:
            username: Username to authenticate
            password: User's password
            
        Returns:
            User information dict if successful, None otherwise
        """
        if not settings.LDAP_ENABLED:
            logger.warning("LDAP authentication is disabled")
            return None
            
        try:
            # Create LDAP server connection
            server = Server(self.server_uri, get_info=ALL)
            
            # Try to bind with user credentials
            user_dn = f"uid={username},{self.user_dn}"
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            
            if conn.bind():
                # Search for user details
                search_filter = self.search_filter.format(username=username)
                conn.search(
                    search_base=self.user_dn,
                    search_filter=search_filter,
                    attributes=['uid', 'cn', 'mail', 'displayName', 'memberOf']
                )
                
                if conn.entries:
                    user_entry = conn.entries[0]
                    user_info = {
                        'username': str(user_entry.uid),
                        'email': str(user_entry.mail) if hasattr(user_entry, 'mail') else None,
                        'full_name': str(user_entry.cn) if hasattr(user_entry, 'cn') else None,
                        'display_name': str(user_entry.displayName) if hasattr(user_entry, 'displayName') else None,
                        'groups': [str(group) for group in user_entry.memberOf] if hasattr(user_entry, 'memberOf') else [],
                        'auth_source': 'ldap'
                    }
                    
                    conn.unbind()
                    logger.info(f"LDAP authentication successful for user: {username}")
                    return user_info
                else:
                    logger.warning(f"User not found in LDAP: {username}")
                    conn.unbind()
                    return None
            else:
                logger.warning(f"LDAP bind failed for user: {username}")
                return None
                
        except LDAPException as e:
            logger.error(f"LDAP authentication error for user {username}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during LDAP authentication: {str(e)}")
            return None
    
    def search_user(self, username: str) -> Optional[Dict]:
        """
        Search for a user in LDAP without authentication
        
        Args:
            username: Username to search for
            
        Returns:
            User information dict if found, None otherwise
        """
        try:
            server = Server(self.server_uri, get_info=ALL)
            conn = Connection(
                server,
                user=self.bind_user,
                password=self.bind_password,
                auto_bind=True
            )
            
            search_filter = self.search_filter.format(username=username)
            conn.search(
                search_base=self.user_dn,
                search_filter=search_filter,
                attributes=['uid', 'cn', 'mail', 'displayName', 'memberOf']
            )
            
            if conn.entries:
                user_entry = conn.entries[0]
                user_info = {
                    'username': str(user_entry.uid),
                    'email': str(user_entry.mail) if hasattr(user_entry, 'mail') else None,
                    'full_name': str(user_entry.cn) if hasattr(user_entry, 'cn') else None,
                    'display_name': str(user_entry.displayName) if hasattr(user_entry, 'displayName') else None,
                    'groups': [str(group) for group in user_entry.memberOf] if hasattr(user_entry, 'memberOf') else []
                }
                conn.unbind()
                return user_info
            else:
                conn.unbind()
                return None
                
        except LDAPException as e:
            logger.error(f"LDAP search error: {str(e)}")
            return None


ldap_auth = LDAPAuthenticator()
