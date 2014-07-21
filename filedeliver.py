import os

import qiniu.conf
import qiniu.rs
import qiniu.io

qiniu.conf.ACCESS_KEY = 'eQ0y6hajOhZRJpc5PdpkTPgq-6X7_lVHbnB98yz6'
qiniu.conf.SECRET_KEY = 'wVGUkLl_GETJb59t5jT--FTsx0r9-q7Yd2rqU0gn'

QINIU_BUCKET_NAME = 'wikty-bookmarks'
QINIU_BUCKET_URL = 'http://wikty-bookmarks.qiniudn.com/'

policy = qiniu.rs.PutPolicy(QINIU_BUCKET_NAME)
uptoken = policy.token()

extra = qiniu.io.PutExtra()
extra.mime_type = 'image/png'

def upload_file(localfile):
    global uptoken, extra
    remote_key = os.path.basename(localfile)
    ret, err = qiniu.io.put_file(uptoken, remote_key, localfile, extra)
    if err is None:
        return QINIU_BUCKET_URL + remote_key


def remove_file(localfile, remote_key):
    ret, err = qiniu.rs.Client().delete(QINIU_BUCKET_NAME, remote_key)
    if err is not None:
        return 'failure'
