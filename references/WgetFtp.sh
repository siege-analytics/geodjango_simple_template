# vip/ExtractBdnShell
set +x;

echo "FTP_HOSTNAME: ${FTP_HOSTNAME}";
echo "FTP_USERNAME: ${FTP_USERNAME}";
echo "FTP_PASSWORD: ${FTP_PASSWORD}";
echo "TARGET_DIR: ${TARGET_DIR}";

mkdir --parents "${TARGET_DIR}/${FTP_USERNAME}";

wget --mirror \
     --no-host-directories \
     --directory-prefix="${TARGET_DIR}/${FTP_USERNAME}" \
     --user="${FTP_USERNAME}" \
     --password="${FTP_PASSWORD}" \
     "${FTP_HOSTNAME}/*";
