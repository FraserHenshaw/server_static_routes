# Windows Create Static route configurations

[![code-style-image]][code-style]
![supported-versions-image]

### Overview

This Script produces the windows commands required to add static routes to servers.

#### Folder Structure

the below folder is the required folder structure to work with this script.

```
📦root
┣ 📂input
┣ 📂next_hops
┣ 📂output
┣ 📜README.md
┣ 📜app.py
┣ 📜utils.py
┗ 📜requirements.txt
```

#### Input

The input file is an excel file based on the output run from an SCCM query. this query outputs the IP address, hostname and all static routes configured on the servers

#### Next Hops

In the next hops folder one or more .txt files are required, these files must consist of the gateways (and masks) that you want to use to filter the input data by. an example of one of these files is below.

```
10.126.106.129/255.255.255.192
10.126.135.33/255.255.255.224
10.126.70.1/255.255.255.0
10.126.71.1/255.255.255.0
10.126.12.1/255.255.255.0
```

#### Output

the output constists of text files broken down by the <i>Domain</i> and <i>Server Name</i> this file contains all of the commands required on that server.

the files will look similar to the below:

```
route -p add 10.124.127.0 mask 255.255.255.0 10.124.126.1 metric 266
route -p add 10.124.127.225 mask 255.255.255.255 10.124.126.1 metric 266
route -p add 10.124.127.255 mask 255.255.255.255 10.124.126.1 metric 266
```

#### Filters

Not all routes are processed, the following are skipped:

```
skipped_names = ["NULL", "LOCALHOST"]

skipped_ips = ["NULL"]

skipped_routes = [
"127.0.0.0",
"127.0.0.1",
"224.0.0.0",
"255.255.255.255",
"127.255.255.255",
]
```

#### Running the script

to run the script make sure you have the required files in both the next_hops and input folder and run app.py

[code-style-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[code-style]: https://github.com/psf/black
[supported-versions-image]: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue.svg
