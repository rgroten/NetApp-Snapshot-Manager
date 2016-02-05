FROM debian:wheezy
MAINTAINER Ryan Groten <rgroten@gmail.com>

# This Dockerfile is a work in progress.  It assumes a lot of configuration
# is already done (by Ansible/etc).  More to come

# Install required packages
RUN apt-get update && apt-get -y install \
  apache2 \
  git \
  libapache2-mod-wsgi \
  python-dev \
  python-ldap \
  python-lxml \
  python-pip \
  unixodbc-dev \
  wget
#  python-setuptools
RUN pip install Flask pyodbc
	
# Configure Apache/WSGI
RUN echo "<VirtualHost *:80>" >> /etc/apache2/mods-available/wsgi.conf
RUN echo "  WSGIPassAuthorization On" >> /etc/apache2/mods-available/wsgi.conf
RUN echo "  WSGIDaemonProcess snapmgr" >> /etc/apache2/mods-available/wsgi.conf
RUN echo "  WSGIScriptAlias / /src/snapmgr/snapmgr.wsgi" >> /etc/apache2/mods-available/wsgi.conf
RUN echo "</VirtualHost>" >> /etc/apache2/mods-available/wsgi.conf
	
EXPOSE 80

# Copy snapmgr source to docker volume
RUN mkdir -p /src/snapmgr
RUN chown www-data:www-data /src/snapmgr
VOLUME ["/src/snapmgr"]
ADD snapmgr /src/snapmgr
RUN chown -R www-data:www-data /src

CMD ["apache2ctl", "-k start -D FOREGROUND"]
