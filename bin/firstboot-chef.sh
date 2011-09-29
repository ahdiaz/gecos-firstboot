#!/bin/bash

chef_server_url=$1
chef_validation_url=$2
user=$3
passwd=$4
node_name=""

chefdir=/etc/chef
chefconf=$chefdir/client.rb
valpem=$chefdir/validation.pem
bakconf=$chefdir/client.rb.gecos-firststart.bak
tmpconf=/tmp/client.rb.tmp
chefclient=`which chef-client`


# Need root user
need_root() {
    if [ 0 != `id -u` ]; then
        echo "You must be root to run this script."
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {

    if [ ! -f $chefconf ]; then
        echo "File not found: "$chefconf
        exit 1
    fi

    if [ "" == "$chef_server_url" ]; then
        echo "URI couldn't be empty."
        exit 1
    fi
}

# Check if Chef is currently configured
check_configured() {
    if [ -f $bakconf ]; then
        echo 1
    else
        echo 0
    fi
    exit 0
}

# Restore the configuration
restore() {

    if [ ! -f $bakconf ]; then
        echo "File not found: "$bakconf
        exit 1
    fi

    mv $chefconf $chefconf".bak"
    mv $bakconf $chefconf

    exit 0
}

# Make a backup
backup() {
    if [ ! -f $bakconf ]; then
        cp $chefconf $bakconf
    fi
}

# Get the pc description
get_pclabel() {
    if [ -f /etc/pclabel ]; then
        node_name=`cat /etc/pclabel`
    else
        node_name=`cat /etc/hostname`
    fi
}

# Update the configuration
update_conf() {

    check_prerequisites
    backup
    get_pclabel

    sed -e s@"^chef_server_url .*"@"chef_server_url \"$chef_server_url\""@g \
        -e s/"^node_name .*"/"node_name $node_name"/g \
        $chefconf > $tmpconf

    # It's posible that some options are commented,
    # be sure to decomment them.
    sed -e s@"^#chef_server_url .*"@"chef_server_url \"$chef_server_url\""@g \
        -e s/"^#node_name .*"/"node_name $node_name"/g \
        $tmpconf > $tmpconf".2"

    mv $tmpconf".2" $tmpconf

    /usr/bin/wget -q --http-user=$user --http-password=$passwd $chef_validation_url
    r_validation=$?

    if [ -f validation.pem ]; then
        mv validation.pem $valpem
    fi

    check_configuration

    mv $tmpconf $chefconf

    # Run chef-client in daemon mode
    if [ -f $chefclient ]; then
        #$chefclient -d 2&>/dev/null
        service chef-client restart
    fi

    echo "The configuration was updated successfully."
    exit 0
}

# Check the changes are valid
check_configuration() {

    r_chef_server_url=`egrep "^chef_server_url \"$chef_server_url\"" $tmpconf`
    r_node_name=`egrep "^node_name \"$node_name\"" $tmpconf`

    if [ "" == "$r_node_name" ]; then
        echo "" >> $tmpconf
        echo "node_name \"$node_name\"" >> $tmpconf
    fi

    if [ "" == "$r_chef_server_url" ]; then
        echo "The configuration couldn't be updated correctly."
        exit 1
    fi

    if [ $r_validation != 0 ]; then
        echo "The validation.pem file couldn't be downloaded correctly."
        exit 1
    fi

    if [ ! -f $valpem ]; then
        echo "The validation.pem file couldn't be moved to $chefdir."
        exit 1
    fi
}

# Restore or update the Chef configuration
case $chef_server_url in
    --restore | -r)
        need_root
        restore
        ;;
    --query | -q)
        check_configured
        ;;
    *)
        need_root
        update_conf
        ;;
esac
