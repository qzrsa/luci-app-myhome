# -*- coding: utf-8 -*-
"""把 luci-app-myhome 打成标准 opkg ipk（无需 OpenWrt buildroot）
ipk = ar 归档: debian-binary + control.tar.gz + data.tar.gz
文件映射: htdocs/ -> /www/, luasrc/ -> /usr/lib/lua/luci/, root/ -> /
"""
import io, os, tarfile, time, gzip, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, '.tmp_ipkg')
DIST = os.path.join(ROOT, 'dist')
PKG, VER, ARCH = 'luci-app-quickstart', '0.12.10-r2', 'all'
MTIME = int(time.time())

def add_tree(tf, src_base, map_to, arc_prefix):
    for dirpath, dirnames, filenames in os.walk(src_base):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, src_base).replace('\\', '/')
            arcname = './' + map_to + rel
            ti = tarfile.TarInfo(arcname)
            ti.size = os.path.getsize(full)
            ti.mtime = MTIME
            ti.mode = 0o755 if fn.endswith('.sh') else 0o644
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = 'root'
            with open(full, 'rb') as f:
                tf.addfile(ti, f)

shutil.rmtree(BUILD, ignore_errors=True)
os.makedirs(os.path.join(BUILD, 'control'))
os.makedirs(DIST, exist_ok=True)

# ---- data.tar.gz（GNU 格式：opkg/busybox 不认 python 默认的 PAX 头）----
data_tgz = os.path.join(BUILD, 'data.tar.gz')
with tarfile.open(data_tgz, 'w:gz', format=tarfile.GNU_FORMAT) as tf:
    add_tree(tf, os.path.join(ROOT, 'htdocs'), 'www/', '')
    add_tree(tf, os.path.join(ROOT, 'luasrc'), 'usr/lib/lua/luci/', '')
    add_tree(tf, os.path.join(ROOT, 'root'), '', '')

# ---- control.tar.gz ----
control = (
    'Package: %s\n'
    'Version: %s\n'
    'Depends: quickstart, luci-app-store\n'
    'Architecture: %s\n'
    'Maintainer: QZRS <1254350772@qq.com>\n'
    'Section: luci\n'
    'Source: https://github.com/qzrsa/luci-app-myhome\n'
    'Description: Customized iStoreOS-style homepage (luci-app-quickstart fork by qzrsa)\n'
) % (PKG, VER, ARCH)
ctrl_path = os.path.join(BUILD, 'control', 'control')
io.open(ctrl_path, 'w', newline='\n').write(control)
ctrl_tgz = os.path.join(BUILD, 'control.tar.gz')
with tarfile.open(ctrl_tgz, 'w:gz', format=tarfile.GNU_FORMAT) as tf:
    tf.add(ctrl_path, arcname='./control')

# ---- 外层：新版 ipk = gzip tar{ ./debian-binary, ./data.tar.gz, ./control.tar.gz } ----
ipk_path = os.path.join(DIST, '%s_%s_%s.ipk' % (PKG, VER, ARCH))
with tarfile.open(ipk_path, 'w:gz', format=tarfile.GNU_FORMAT) as outer:
    for name, path in [('debian-binary', None), ('data.tar.gz', data_tgz), ('control.tar.gz', ctrl_tgz)]:
        if name == 'debian-binary':
            payload = b'2.0\n'
            ti = tarfile.TarInfo('./' + name)
            ti.size = len(payload)
            ti.mtime = MTIME; ti.uid = ti.gid = 0; ti.uname = ti.gname = 'root'; ti.mode = 0o644
            import io as _io
            outer.addfile(ti, _io.BytesIO(payload))
        else:
            outer.add(path, arcname='./' + name)

print('ipk 已生成:', ipk_path, os.path.getsize(ipk_path), 'bytes')
