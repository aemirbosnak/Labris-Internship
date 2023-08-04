FROM tgagor/centos-stream:stream8

# Install Remi repository
RUN yum install -y https://rpms.remirepo.net/enterprise/remi-release-8.rpm \
    && yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

# Install build tools and dependencies
RUN yum install -y gcc-c++ flex bison yajl curl-devel curl zlib-devel  \
    pcre-devel autoconf automake git make libxml2-devel pkgconfig libtool  \
    httpd-devel redhat-rpm-config wget openssl openssl-devel \
    && yum -y --enablerepo=powertools install doxygen yajl-devel \
    && yum -y --enablerepo=remi install GeoIP-devel

# Install ModSecurity
ARG MODSEC_VERSION=v3/master
ENV MODSEC_INSTALL_PATH=/opt/modsec

WORKDIR $MODSEC_INSTALL_PATH
RUN git clone --depth 1 -b $MODSEC_VERSION --single-branch https://github.com/SpiderLabs/ModSecurity
WORKDIR $MODSEC_INSTALL_PATH/ModSecurity
RUN git submodule init && git submodule update
RUN ./build.sh && ./configure && make && make install

# Install NGINX and ModSecurity NGINX connector
ENV NGINX_VERSION=1.17.6
ENV NGINX_INSTALL_PATH=/usr/local/nginx

WORKDIR $MODSEC_INSTALL_PATH
RUN git clone https://github.com/SpiderLabs/ModSecurity-nginx.git

WORKDIR /opt
RUN wget https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar xzf nginx-${NGINX_VERSION}.tar.gz

WORKDIR /opt/nginx-${NGINX_VERSION}
RUN ./configure --with-pcre-jit --with-debug --with-http_ssl_module  \
    --with-http_v2_module --with-http_realip_module  \
    --add-module=${MODSEC_INSTALL_PATH}/ModSecurity-nginx && \
    make && make install

# Configure nginx
COPY nginx.service /etc/systemd/system/
RUN ln -s ${NGINX_INSTALL_PATH}/sbin/nginx /usr/sbin/

# OWASP Core Rule Set
RUN git clone https://github.com/coreruleset/coreruleset.git ${NGINX_INSTALL_PATH}/conf/owasp-crs && \
    cp ${NGINX_INSTALL_PATH}/conf/owasp-crs/crs-setup.conf.example ${NGINX_INSTALL_PATH}/conf/owasp-crs/crs-setup.conf

# Configure nginx with modsecurity
COPY modsecurity.conf ${NGINX_INSTALL_PATH}/conf/modsecurity.conf
RUN cp ${MODSEC_INSTALL_PATH}/ModSecurity/unicode.mapping ${NGINX_INSTALL_PATH}/conf
RUN mkdir -p /var/log/nginx

# Configure SSL server
RUN mkdir /etc/ssl/private && \
    chmod 700 /etc/ssl/private && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=TR/ST=Ankara/L=Ankara/O=Labris/CN=192.168.0.178" && \
    openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# Copy NGINX configuration
COPY nginx.conf ${NGINX_INSTALL_PATH}/conf/nginx.conf

# Expose ports
EXPOSE 80
EXPOSE 443

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
