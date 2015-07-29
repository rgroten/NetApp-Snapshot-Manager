

Features
=============

This web-based AngularJS and Flask application allows users to perform simple operations on NetApp volumes.  

Operations that this app provide include: 

	- Displaying volumes and their snapshots
	- Creating snapshots with specified or default names
	- Renaming snapshots
	- Deleting snapshots
	- Restoring snapshots

More specific features LDAP authentication, RFCChecker (using sql query) 
# Software Pre-requisites

	- See requirements.txt for list of python requirements from pip
	- xml2json js library is used (https://code.google.com/p/x2js/)
	- ngProgress AngularJS progressbar (http://victorbjelkholm.github.io/ngProgress/)
	- NetApp python SDK libraries			# NaServer.py, NaElement.py.  Tested with SDK5. Available from NetApp

Deployment
==========

No building required, simply use git to checkout the project where you want to run from (ie: /var/www/html)
After checking out the project, edit the snapmgr/config.ini to set the connection info for your NetApp SVM.
deploy_snapmgr.sh is a wrapper script you can use to deploy snapmgr (and update it subsequently)

## config.ini Details - see example config.ini included in project for syntax

1. [DEFAULT]

	- VolFilters	: is a list of strings used to exclude volumes from being displayed on the page
	- Debug		: Debug mode enables additional logging on the server side. It also enables Flask debugging and should be set to False in real deployments
	- AuthRequired	: If true the LDAP connection info needs to be supplied. When a user hits the page they will need to input their LDAP username/password to access the page
	- LdapServer	: Format is ldap(s)://<ldap.example.com>
	- BaseUserDn	: Base search DN for LDAP users
	- TLSCACertFile	: If using LDAPS a path to the cacert may be required
	- RFCRequired	: If true for a specific environment, the server will check an RFC Database to ensure that an RFC is created before allowing a Snapshot Restore to proceed

2. [GENERAL]

	- Environments	: This is a list of NetApp environments to allow the user to connect to.  Each string in this list must have a subsection with connection info.

3. [RFCDBCONN]

	- Server		: Server where RFC Database runs
	- Port			: Port to connect to the RFC Database on 
	- DB			: Name of the RFC database 
	- User/Password	: User/Password of user who has access to RFC database (read-only access is enough)
	- Driver		: Driver used by pyodbc to connect to database (ie: PostgreSQL, MySQL, etc)

4. [ENVIRONMENTS]
One [ENV] section is required for each string in Environments parameter. 

These parameters override anything specified in the DEFAULT section.

	- NAHost		: hostname or IP address of NetApp SVM to connect to
	- User/Password	: User/Password of user who has been given access to ONTAP within NetApp SVM
	- Debug			: You can set parameters in each environment section. 
		For example, set Debug: True in [TEST] section to enable debugging for only the TEST environment. 
		Don't include Debug in the [PROD] and it will default to the Debug value set in [DEFAULT] section 

This app requires the NetApp python libraries (NaServer.py, NaElement.py) to communicate with the NetApp SVM. These libraries are not included in this project but are available from the vendor.

## Dump of installation/setup (on Fedora 22)

```bash
[rgroten@rgroten-fed ~] $ git clone rlx7009:/git/NetAppSnapManager
[rgroten@rgroten-fed ~] $ cd NetAppSnapManager
[rgroten@rgroten-fed NetAppSnapManager] $ sudo dnf install python-virtualenv gcc-c++ openldap-devel unixODBC-devel libxml2-devel libxslt-devel
[rgroten@rgroten-fed NetAppSnapManager] $ virtualenv env
[rgroten@rgroten-fed NetAppSnapManager] $ source env/bin/activate
(env)[rgroten@rgroten-fed NetAppSnapManager] $ pip install -r snapmgr/requirements.txt
[rgroten@rgroten-fed NetAppSnapManager] $ ./deploy_snapmgr.sh
```

For simple testing purposes, you can now run the app using Flask's built-in webserver (NOT to be used for real/prod environments):

```bash
(env)[rgroten@rgroten-fed NetAppSnapManager] $ cd snapmgr
(env)[rgroten@rgroten-fed snapmgr] $ python snapmgr.py
 * Running on http://127.0.0.1:5001/ (Press CTRL+C to quit)
 * Restarting with stat
```
Contact
=======

For help or questions please email me

License
=======
SnapManager - Web client for performing snapshot tasks on NetApp Volumes using NetApp ONTAP

Copyright (C) 2015  Ryan Groten

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
