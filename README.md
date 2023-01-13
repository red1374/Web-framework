# Web-framework
WSGI Python web framework

To start working with the service open terminal, go to the project working directory and run gunicorn server:

<code># cd /mnt/disk_label/path_to_project/</code>

<code># gunicorn -b 0.0.0.0:8000 main:app</code>

Then open your browser and type ip address of your network interface with port 8000

For example:

<code># ip addr

eth0:
   ...
    inet **172.28.79.16**/20 brd 172.28.79.255 scope global eth0
   ...
</code>

<code># 172.31.156.253:8000 </code>
