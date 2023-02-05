# Web-framework
WSGI Python web framework

O. Before starting the Project you need to create a database by executing script <code>/db/create_db.py</code>.

I. To start working with the service open terminal, go to the project working directory and run gunicorn server:

<code># cd /mnt/disk_label/path_to_project/</code>

<code># gunicorn -b 0.0.0.0:8000 main:app</code>


You can use extra params for gunicorn
- <code>--reload</code> - set key to reload server on code changed
- <code>--error-logfile <path_to_log_file></code> - set this key to specify a log file
- <code>--capture-output</code> - set this key to capture stdout/stderr streams and redirect them to log file
- <code>--log-level</code> - select messages type to store at log file ( debug, info, warning, error, critical)
- <code>-t INT</code> or <code>--timeout INT</code> - to set worker timeout value
- <code>-w INT</code> or <code>--workers INT</code> - to set workers count

---
II. Then open your browser and type ip address of your network interface with port 8000

For example:

<code># ip addr

eth0:
   ...
    inet **172.28.79.16**/20 brd 172.28.79.255 scope global eth0
   ...
</code>

<code># 172.31.156.253:8000 </code>

---
III. There is two more WSGI applications to run:
- Fake application. On any request returns a string **Hello from Fake** 
<code>gunicorn -b 0.0.0.0:8000 main:fake_app</code>
- Logger application.  Returns short request information:
<code>gunicorn -b 0.0.0.0:8000 main:logger_app</code>