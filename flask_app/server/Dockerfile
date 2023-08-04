FROM tgagor/centos-stream:stream8

# Install build tools and dependencies
RUN yum install -y gcc-c++ flex bison yajl curl-devel curl zlib-devel pcre-devel autoconf automake git curl make libxml2-devel pkgconfig libtool httpd-devel redhat-rpm-config git wget openssl openssl-devel

# Install EPEL and Remi
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
RUN yum install -y https://rpms.remirepo.net/enterprise/remi-release-8.rpm

# Install GeoIP module
RUN yum -y --enablerepo=powertools install -y doxygen yajl-devel
RUN yum -y --enablerepo=remi install -y GeoIP-devel

# Install ModSecurity
RUN mkdir -p /opt/modsec

WORKDIR /opt/modsec
RUN git clone --depth 1 -b v3/master --single-branch https://github.com/SpiderLabs/ModSecurity

WORKDIR /opt/modsec/ModSecurity
RUN git submodule init
RUN git submodule update # url error 503

RUN ./build.sh
RUN ./configure
RUN make
RUN make install

# Compile nginx
WORKDIR /opt/modsec
RUN git clone https://github.com/SpiderLabs/ModSecurity-nginx.git

WORKDIR /opt
RUN wget https://nginx.org/download/nginx-1.17.6.tar.gz
RUN tar xzf nginx-1.17.6.tar.gz

WORKDIR /opt/nginx-1.17.6
RUN ./configure --with-pcre-jit --with-debug --with-http_ssl_module --with-http_v2_module --with-http_realip_module --add-module=/opt/modsec/ModSecurity-nginx
RUN make
RUN make install

# Configure nginx
COPY nginx.service /etc/systemd/system/
RUN ln -s /usr/local/nginx/sbin/nginx /usr/sbin/

# OWASP Core Rule Set
RUN git clone https://github.com/coreruleset/coreruleset.git /usr/local/nginx/conf/owasp-crs
RUN cp /usr/local/nginx/conf/owasp-crs/crs-setup.conf.example /usr/local/nginx/conf/owasp-crs/crs-setup.conf

# Configure nginx with modsecurity
RUN cp /opt/modsec/ModSecurity/modsecurity.conf-recommended /usr/local/nginx/conf/modsecurity.conf
RUN cp /opt/modsec/ModSecurity/unicode.mapping /usr/local/nginx/conf/
RUN mkdir -p /var/log/nginx

# Modsecurity configuration
COPY modsecurity.conf /usr/local/nginx/conf/modsecurity.conf

# Configure SSL server
RUN mkdir /etc/ssl/private
RUN chmod 700 /etc/ssl/private

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=TR/ST=Ankara/L=Ankara/O=Labris/CN=192.168.0.178"
RUN openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

COPY nginx.conf /usr/local/nginx/conf/nginx.conf

EXPOSE 80
EXPOSE 443

CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
