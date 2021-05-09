while getopts u: flag
do
    case "${flag}" in
        u) url=${OPTARG};;
    esac
done



echo "$url," >> history.txt

rm /var/www/html/*.mp4

# save in movies directory with datetime 
DATETIME=$(date +%F-%T)
youtube-dl -f mp4 $url -o /var/www/html/movies/$DATETIME.mp4

cp /var/www/html/movies/$DATETIME.mp4 /var/www/html/movie.mp4

systemctl reload nginx