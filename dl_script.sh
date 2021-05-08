while getopts u: flag
do
    case "${flag}" in
        u) url=${OPTARG};;
    esac
done


rm /var/www/html/movie.mp4

echo "$url" >> history.txt

youtube-dl -f mp4 $url -o /var/www/html/movie.mp4

systemctl reload nginx
