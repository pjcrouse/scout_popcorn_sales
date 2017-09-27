#!/bin/bash
# restarts nginx, superviosor, flask and bokeh 
service nginx restart
service supervisor restart
supervisorctl restart flask
supervisorctl restart bokeh_serve
