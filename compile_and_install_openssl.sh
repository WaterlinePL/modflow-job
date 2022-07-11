#!/bin/bash
wget --no-check-certificate https://www.openssl.org/source/openssl-1.1.1q.tar.gz
tar -xf openssl-1.1.1q.tar.gz
cd openssl-1.1.1q
./config --prefix=/usr/local/ssl --openssldir=/usr/local/ssl shared zlib
make

make install
echo "/usr/local/ssl/lib" > /etc/ld.so.conf.d/openssl-1.1.1q.conf
ldconfig -v
mv /usr/bin/c_rehash /usr/bin/c_rehash.old
mv /usr/bin/openssl /usr/bin/openssl.old
ln -s /usr/local/ssl/bin/openssl /usr/bin/openssl
ln -s /usr/local/ssl/bin/c_rehash /usr/bin/c_rehash

# Cleanup
cd /
rm -r /openssl-1.1.1q
rm openssl-1.1.1q.tar.gz
