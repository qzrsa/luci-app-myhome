# luci-app-myhome

基于 [linkease/luci-app-quickstart](https://github.com/linkease/nas-packages-luci)（iStoreOS 大首页）的**个人定制版**。

## 改动内容

（逐项记录中……）

## 说明

- 包名保持 `luci-app-quickstart`，版本号高于官方版时可直接 opkg 覆盖安装，无文件冲突。
- 前端产物为编译后的 `htdocs/luci-static/quickstart/{index.js,vendor.js,style.css}`，样式定制优先改 `style.css`（使用 CSS 变量）。
- 编译 ipk：将本目录放入 OpenWrt buildroot 的 `feeds/luci/applications/` 下 `make package/luci-app-quickstart/compile`。

## 上游

- 源码：linkease/nas-packages-luci `luci/luci-app-quickstart`
- 后端：linkease/quickstart (Go)
