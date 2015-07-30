# PATH to deployment directory of app
GIT_PATH=$(pwd)
APP_PATH=$GIT_PATH/snapmgr

if [ ! -d $APP_PATH ]; then
    echo "Error: $APP_PATH not found"
    exit 1
fi

# Backup the existing config.ini
# To deploy a new config.ini create config.ini.new and place it in snapmgr/ dir before running deploy_snapmgr.sh
if [ -s $APP_PATH/config.ini.new ]; then
    mv $APP_PATH/config.ini.new /tmp
elif [ -s $APP_PATH/config.ini ]; then
    echo "Backing up deployed config.ini"
    cp $APP_PATH/config.ini /tmp
fi

# Reset to tagged version
if [ -n "$1" ]; then 
    cd $GIT_PATH
    git reset --hard $1
else 
	# get the latest
    git reset --hard
    git pull
fi

# Stop web service
if [ $USER = "root" ]; then
    service httpd stop
else
    sudo service httpd stop
fi

# Fix path to config files (make sure full path to config.ini is set - required for WSGI)
sed -i "s,\".*config.ini,\"$APP_PATH/config.ini,g" $APP_PATH/*.py

# Set path to log (full path required for WSGI)
sed -i "s,\".*snapmgr.log,\"$APP_PATH/snapmgr.log,g" $APP_PATH/*.py

if [ -s /tmp/config.ini.new ]; then
    echo "New version of config.ini found, will replace"
    mv $APP_PATH/config.ini $APP_PATH/config.ini.backup
    mv /tmp/config.ini.new $APP_PATH/config.ini
elif [ -s /tmp/config.ini ]; then
    echo "Restoring original config.ini"
    mv $APP_PATH/config.ini $APP_PATH/config.ini.backup
    mv /tmp/config.ini $APP_PATH/config.ini
fi

# Download required javascript dependencies
wget -O $APP_PATH/static/js/ngProgress.min.js https://raw.githubusercontent.com/VictorBjelkholm/ngProgress/master/build/ngprogress.min.js
wget -O $APP_PATH/static/js/xml2json.min.js https://x2js.googlecode.com/hg/xml2json.min.js
wget -O $APP_PATH/static/css/ngProgress.css https://raw.githubusercontent.com/VictorBjelkholm/ngProgress/master/ngProgress.css

# Get NetApp SDK libraries from staging area
cp -f ~/staging/Na*.py $APP_PATH/

# Restrict permissions
chgrp -R apache $GIT_PATH
chmod -R o-rwx $GIT_PATH
chmod g+rwx $APP_PATH

# Restart web service
if [ $USER = "root" ]; then
    service httpd start
else
    sudo service httpd start
fi
