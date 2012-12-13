Xamin UMS
=========

Upstream managment system

Master
=======

 * Add source :
   ```ums config add wheezy/main binary-amd64 stable/main "xaminkey <xaminsign@xamin.ir>" --priority 1```
 * Check source :
   ```ums config show```
 * Update :
   ```ums update```
 * Add a package :
   ```ums add stable/main apache2 --level 3```
 
Slave (Downloader)
==================
 * Run download watch :
   ```ums download uniq_id /target/dir```
 