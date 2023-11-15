
wait_for_it=$(dirname "$0")/wait-for-it.sh

chmod +x $wait_for_it
chmod +x $1

$wait_for_it -h $POSTGRES_HOST -p $POSTGRES_PORT -- $1