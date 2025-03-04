// DistanceTool.js
import L from 'leaflet';

export default class DistanceTool {
    constructor(map, options = {}) {
        if (!map) {
            throw new Error('Map instance is required');
        }

        this._map = map;

        // 合并默认选项
        this._opts = {
            followText: '单击确定地点，双击结束',
            unit: 'metric',
            lineColor: '#191dff',
            lineStroke: 2,
            opacity: 100,
            lineStyle: 'solid',
            cursor: 'crosshair',
            ...options
        };

        // 状态变量
        this._isOpen = false;
        this._points = [];
        this._paths = [];
        this._segDistance = [];
        this._overlays = [];
        this._tempLine = null;
        this._followTitle = null;

        // 保存所有测距集合
        this._measurementSets = [];
        this._currentMeasurement = null;

        // 单位定义
        this._units = {
            metric: {
                name: 'metric',
                conv: 1,
                incon: 1000,
                u1: '米',
                u2: '公里'
            },
            us: {
                name: 'us',
                conv: 3.2808,
                incon: 5279.856,
                u1: '英尺',
                u2: '英里'
            }
        };

        // 绑定事件处理函数
        this._handleMapClick = this._handleMapClick.bind(this);
        this._handleMouseMove = this._handleMouseMove.bind(this);
        this._handleMapDblClick = this._handleMapDblClick.bind(this);
        this._handleKeyDown = this._handleKeyDown.bind(this);

        // 创建鼠标跟随提示框
        this._createFollowTitle();
    }

    // 创建鼠标跟随的文字提示
    _createFollowTitle() {
        this._followTitle = L.marker([0, 0], {
            icon: L.divIcon({
                className: 'leaflet-distance-tooltip',
                html: `<span style="color:${this._opts.lineColor}">单击确定起点</span>`,
                iconSize: [80, 18],
                iconAnchor: [-10, 0]
            }),
            interactive: false,
            zIndexOffset: 1000
        });
    }

    // 开启测距
    open() {
        if (this._isOpen) {
            return true;
        }

        this._isOpen = true;


        // 初始化当前测距
        this._initData();
        this._currentMeasurement = {
            points: [],
            paths: [],
            segDistance: [],
            dots: [],
            overlays: [],
            id: Date.now() // 唯一ID
        };

        // 设置鼠标样式
        this._updateMapCursor(this._opts.cursor);

        // 绑定事件
        this._map.on('click', this._handleMapClick);
        this._map.on('mousemove', this._handleMouseMove);
        this._map.on('dblclick', this._handleMapDblClick);
        document.addEventListener('keydown', this._handleKeyDown);

        // 显示跟随提示
        this._followTitle.addTo(this._map);

        return true;
    }

    // 关闭测距
    close() {
        if (!this._isOpen) {
            return;
        }

        this._isOpen = false;

        // 移除事件监听
        this._map.off('click', this._handleMapClick);
        this._map.off('mousemove', this._handleMouseMove);
        this._map.off('dblclick', this._handleMapDblClick);
        document.removeEventListener('keydown', this._handleKeyDown);

        // 处理最后的操作
        if (this._points.length < 2) {
            this._clearCurData();
        } else {
            if (this._tempLine) {
                this._map.removeLayer(this._tempLine);
                this._tempLine = null;
            }
            this._processLastOp();

            // 保存当前测距到集合中
            if (this._currentMeasurement) {
                this._measurementSets.push({...this._currentMeasurement});
            }
        }

        // 移除跟随提示
        if (this._followTitle) {
            this._map.removeLayer(this._followTitle);
        }

        // 恢复鼠标样式
        this._updateMapCursor('');
    }

    // 清除当前测距数据
    _clearCurData() {
        this._overlays.forEach(overlay => {
            if (overlay && this._map) {
                this._map.removeLayer(overlay);
            }
        });

        this._initData();
    }

    // 清除特定的测距线
    _clearSpecificMeasurement(measurementId) {
        // 查找对应ID的测距集
        const measurementIndex = this._measurementSets.findIndex(m => m.id === measurementId);

        if (measurementIndex !== -1) {
            const measurement = this._measurementSets[measurementIndex];

            // 清除所有相关覆盖物
            measurement.overlays.forEach(overlay => {
                if (overlay && this._map) {
                    this._map.removeLayer(overlay);
                }
            });

            // 从集合中移除
            this._measurementSets.splice(measurementIndex, 1);
        }
    }

    // 清除所有测距数据
    clearAll() {
        // 清除当前测距
        this._clearCurData();

        // 清除所有已保存的测距
        this._measurementSets.forEach(measurement => {
            measurement.overlays.forEach(overlay => {
                if (overlay && this._map) {
                    this._map.removeLayer(overlay);
                }
            });
        });

        this._measurementSets = [];
    }

    // 初始化数据
    _initData() {
        this._points = [];
        this._paths = [];
        this._segDistance = [];
        this._overlays = [];
        this._tempLine = null;
    }

    // 处理地图点击
    _handleMapClick(e) {
        if (!this._isOpen) {
            return;
        }

        const newPoint = e.latlng;

        // 如果有前一个点，检查是否与前一点距离太近
        if (this._points.length > 0) {
            const lastPoint = this._points[this._points.length - 1];
            const pixelDist = this._map.latLngToLayerPoint(lastPoint).distanceTo(
                this._map.latLngToLayerPoint(newPoint)
            );

            // 如果距离小于5像素，忽略该点击
            if (pixelDist < 5) {
                return;
            }
        }

        // 添加点
        this._points.push(newPoint);
        this._currentMeasurement.points.push(newPoint);

        // 添加节点标记
        const dot = this._addSecPoint(newPoint);
        this._currentMeasurement.dots.push(dot);

        // 调整跟踪鼠标的标签
        if (this._paths.length === 0) {
            this._updateFollowTitle(1, this._opts.followText, this._getTotalDistance());
        }

        // 创建新的路径
        let pathLatLngs = [];
        if (this._points.length > 1) {
            const prevPoint = this._points[this._points.length - 2];
            pathLatLngs = [prevPoint, newPoint];
        } else {
            pathLatLngs = [newPoint, newPoint]; // 第一个点时创建零长度线
        }

        const path = L.polyline(pathLatLngs, {
            color: this._opts.lineColor,
            weight: this._opts.lineStroke,
            opacity: this._opts.opacity,
            dashArray: this._opts.lineStyle === 'dashed' ? '5, 10' : null
        }).addTo(this._map);

        this._paths.push(path);
        this._overlays.push(path);
        this._currentMeasurement.paths.push(path);
        this._currentMeasurement.overlays.push(path);

        // 生成节点旁边的距离显示框
        let disText = '';
        if (this._points.length > 1) {
            // 非起点的节点，显示当前的距离
            const prevPoint = this._points[this._points.length - 2];
            const segDis = this._setSegDistance(prevPoint, newPoint);
            this._currentMeasurement.segDistance.push(segDis);

            const meters = this._getTotalDistance();
            disText = this._formatDistance(meters);

            // 添加线段中点的距离标签
            const midPoint = L.latLng(
                (prevPoint.lat + newPoint.lat) / 2,
                (prevPoint.lng + newPoint.lng) / 2
            );

            const segmentLabel = L.marker(midPoint, {
                icon: L.divIcon({
                    className: 'leaflet-segment-label',
                    html: `<div><span style=color:${this._opts.lineColor}>${this._formatDistance(segDis)}</span></div>`,
                    iconSize: [80, 20],
                    iconAnchor: [40, 10]
                }),
                interactive: false
            }).addTo(this._map);

            this._overlays.push(segmentLabel);
            this._currentMeasurement.overlays.push(segmentLabel);
        } else {
            disText = '起点';
        }

        const disLabel = L.marker(newPoint, {
            icon: L.divIcon({
                className: 'leaflet-distance-label',
                html: `<div>${disText}</div>`,
                iconSize: [80, 20],
                iconAnchor: [40, 20]
            }),
            interactive: false
        }).addTo(this._map);

        this._overlays.push(disLabel);
        this._currentMeasurement.overlays.push(disLabel);
        newPoint.disLabel = disLabel;

        // 触发添加点事件
        this._fire('onaddpoint', {
            point: newPoint,
            pixel: this._map.latLngToLayerPoint(newPoint),
            index: this._points.length - 1,
            distance: this._getTotalDistance().toFixed(0)
        });
    }

    // 处理鼠标移动
    _handleMouseMove(e) {
        if (!this._isOpen) {
            return;
        }

        // 更新跟随标签位置
        this._followTitle.setLatLng(e.latlng);

        // 如果有测量点，更新临时线
        if (this._points.length > 0) {
            const lastPoint = this._points[this._points.length - 1];
            const mousePoint = e.latlng;

            // 更新或创建临时线
            if (this._tempLine) {
                this._tempLine.setLatLngs([lastPoint, mousePoint]);
            } else {
                this._tempLine = L.polyline([lastPoint, mousePoint], {
                    color: this._opts.lineColor,
                    weight: this._opts.lineStroke,
                    opacity: this._opts.opacity,
                    dashArray: '5, 10'
                }).addTo(this._map);
                this._overlays.push(this._tempLine);
            }

            // 更新距离提示
            const tempDistance = this._map.distance(lastPoint, mousePoint);
            const totalWithTemp = this._getTotalDistance() + tempDistance;
            this._updateInstDis(totalWithTemp);
        }
    }

    // 处理双击结束测量 - 阻止冒泡
    _handleMapDblClick(e) {
        if (!this._isOpen) {
            return;
        }

        // 阻止事件冒泡，避免缩放地图
        L.DomEvent.stopPropagation(e);
        L.DomEvent.preventDefault(e);

        // 触发测距结束事件
        this._dispatchLastEvent();

        // 关闭测距
        setTimeout(() => {
            this.close();
        }, 50);
    }

    // 处理键盘按键
    _handleKeyDown(e) {
        if (!this._isOpen) {
            return;
        }

        // ESC键退出测距
        if (e.keyCode === 27) {
            this._clearCurData();
            setTimeout(() => {
                this.close();
            }, 50);
        }
    }

    // 添加测距节点
    _addSecPoint(point) {
        const markerIcon = L.divIcon({
            className: 'distance-node-icon',
            html: `<div style="width:8px;height:8px;background:white;border-radius:50%;border:2px solid ${this._opts.lineColor};"></div>`,
            iconSize: [12, 12],
            iconAnchor: [6, 6]
        });

        const marker = L.marker(point, {
            icon: markerIcon,
            draggable: false
        }).addTo(this._map);

        this._overlays.push(marker);
        this._currentMeasurement.overlays.push(marker);

        return marker;
    }

    // 计算两点之间距离并存储
    _setSegDistance(pt0, pt1) {
        if (!pt0 || !pt1) {
            return 0;
        }

        const dis = this._map.distance(pt0, pt1);
        this._segDistance.push(dis);
        return dis;
    }

    // 获取总距离
    _getTotalDistance() {
        return this._segDistance.reduce((total, dis) => total + dis, 0);
    }

    // 单位转换
    _convertUnit(num, unit) {
        unit = unit || 'metric';
        if (this._units[unit]) {
            return num * this._units[unit].conv;
        }
        return num;
    }

    // 格式化距离字符串
    _formatDistance(distance) {
        const unit = this._opts.unit;
        let unitText = this._units[unit].u1;
        let dis = this._convertUnit(distance, unit);

        if (dis > this._units[unit].incon) {
            dis = dis / this._units[unit].incon;
            unitText = this._units[unit].u2;
            dis = dis.toFixed(1);
        } else {
            dis = dis.toFixed(0);
        }

        return dis + unitText;
    }

    // 更新地图鼠标样式
    _updateMapCursor(cursor) {
        if (this._map._container) {
            this._map._container.style.cursor = cursor;
        }
    }

    // 更新跟随提示内容
    _updateFollowTitle(type, text, distance) {
        let content = '';

        if (type === 1) {
            // 测距过程中的提示
            const unit = this._opts.unit;
            let unitText = this._units[unit].u1;
            let dis = this._convertUnit(distance, unit);

            if (dis > this._units[unit].incon) {
                dis = dis / this._units[unit].incon;
                unitText = this._units[unit].u2;
                dis = dis.toFixed(1);
            } else {
                dis = dis.toFixed(0);
            }

            content = `总长: <span style="color:${this._opts.lineColor};font-weight:bold">${dis}</span>${unitText}<br /><span style="color:#7a7a7a">${text}</span>`;
        } else if (type === 2) {
            // 结束时的总距离展示
            const unit = this._opts.unit;
            let unitText = this._units[unit].u1;
            let dis = this._convertUnit(this._getTotalDistance(), unit);

            if (dis > this._units[unit].incon) {
                dis = dis / this._units[unit].incon;
                unitText = this._units[unit].u2;
                dis = dis.toFixed(1);
            } else {
                dis = dis.toFixed(0);
            }

            content = `总长: <span style="color:${this._opts.lineColor};border: 1px solid ${this._opts.lineColor};font-weight:bold">${dis}</span>${unitText}`;
        } else {
            content = '单击确定起点';
        }

        this._followTitle.setIcon(L.divIcon({
            className: 'leaflet-distance-tooltip',
            html: content,
            iconSize: [140, 40],
            iconAnchor: [-15, 15]
        }));
    }

    // 更新实时距离显示
    _updateInstDis(dis) {
        const unit = this._opts.unit;
        let unitText = this._units[unit].u1;
        let distance = this._convertUnit(dis, unit);

        if (distance > this._units[unit].incon) {
            distance = distance / this._units[unit].incon;
            unitText = this._units[unit].u2;
            distance = distance.toFixed(1);
        } else {
            distance = distance.toFixed(0);
        }

        const content = `总长: <span style="color:${this._opts.lineColor};font-weight:bold">${distance}</span>${unitText}<br /><span style="color:#7a7a7a">${this._opts.followText}</span>`;

        this._followTitle.setIcon(L.divIcon({
            className: 'leaflet-distance-tooltip',
            html: content,
            iconSize: [140, 40],
            iconAnchor: [-15, 15]
        }));
    }

    // 处理最后一步操作
    _processLastOp() {
        if (this._points.length < 2) {
            return;
        }

        // 添加总距离标签
        const lastPoint = this._points[this._points.length - 1];
        const totalDis = this._getTotalDistance();

        // 确定标签偏移方向
        let disOffset = [-5, -35];
        let btnOffset = [14, 0];

        if (this._points.length >= 2) {
            const prevPoint = this._points[this._points.length - 2];

            const lastPx = this._map.latLngToLayerPoint(lastPoint);
            const prevPx = this._map.latLngToLayerPoint(prevPoint);

            if (lastPx.y - prevPx.y >= 0) {
                // 距离位于下端
                disOffset = [-5, 11];
            }

            if (lastPx.x - prevPx.x >= 0) {
                // 按钮位于右侧
                btnOffset = [14, 0];
            } else {
                // 按钮位于左侧
                btnOffset = [-14, 0];
            }
        }

        // 添加总距离标签
        const totalLabel = L.marker(lastPoint, {
            icon: L.divIcon({
                className: 'leaflet-total-distance-label',
                html: `总长: <span style="color:${this._opts.lineColor};font-weight:bold">${this._formatDistance(totalDis)}</span>`,
                iconSize: [100, 20],
                iconAnchor: [-15, -5]
            }),
            interactive: false
        }).addTo(this._map);

        this._overlays.push(totalLabel);
        this._currentMeasurement.overlays.push(totalLabel);

        // 添加关闭按钮，关键点：保存对应的测距ID
        const closeIcon = L.divIcon({
            className: 'leaflet-distance-close-button',
            html: `<div style="background-color: white; border: 1px solid ${this._opts.lineColor}; border-radius: 2px; cursor: pointer; width: 14px; height: 14px; text-align: center; line-height: 14px;"><span style="color:${this._opts.lineColor};font-weight:bold">×</span></div>`,
            iconSize: [120, 14],
            iconAnchor: [-15, 15]
        });

        const closeButton = L.marker([lastPoint.lat, lastPoint.lng], {
            icon: closeIcon,
            interactive: true,
            zIndexOffset: 1000
        }).addTo(this._map);


        // 保存测距ID到按钮
        closeButton.measurementId = this._currentMeasurement.id;

        // 为关闭按钮添加点击事件
        const self = this;
        L.DomEvent.on(closeButton._icon, 'click', function(e) {
            L.DomEvent.stopPropagation(e);

            // 清除特定的测距线
            self._clearSpecificMeasurement(closeButton.measurementId);

            // 触发移除测距线事件
            self._fire('onremovepolyline', {});
        });

        this._overlays.push(closeButton);
        this._currentMeasurement.overlays.push(closeButton);
    }

    // 派发最后事件
    _dispatchLastEvent() {
        this._fire('ondrawend', {
            points: this._points.slice(0),
            overlays: this._paths.slice(0),
            distance: this._getTotalDistance().toFixed(0)
        });
    }

    // 触发事件
    _fire(eventType, data) {
        const event = new CustomEvent(eventType, {
            detail: data
        });

        document.dispatchEvent(event);
    }

    // 添加事件监听
    addEventListener(eventType, handler) {
        document.addEventListener(eventType, (e) => {
            handler(e.detail);
        });
    }

    // 移除事件监听
    removeEventListener(eventType, handler) {
        document.removeEventListener(eventType, handler);
    }
}
