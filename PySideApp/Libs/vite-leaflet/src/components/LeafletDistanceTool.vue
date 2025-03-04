<template>
  <div class="leaflet-distance-tool-container">
    <div v-if="showControls" class="distance-tool-controls">
      <button @click="toggleMeasure" class="distance-tool-btn">
        {{ isOpen ? '结束测距' : '开始测距' }}
      </button>
    </div>
  </div>
</template>

<script>
import L from 'leaflet';

export default {
  name: 'LeafletDistanceTool',
  props: {
    mapInstance: {
      type: Object,
      required: true
    },
    showControls: {
      type: Boolean,
      default: false
    },
    followText: {
      type: String,
      default: '单击确定地点，双击结束'
    },
    unit: {
      type: String,
      default: 'metric',
      validator: value => ['metric', 'us'].includes(value)
    },
    lineColor: {
      type: String,
      default: '#ff6319'
    },
    lineStroke: {
      type: Number,
      default: 2
    },
    opacity: {
      type: Number,
      default: 0.8
    },
    lineStyle: {
      type: String,
      default: 'solid',
      validator: value => ['solid', 'dashed'].includes(value)
    },
    cursor: {
      type: String,
      default: 'crosshair'
    }
  },
  data() {
    return {
      isOpen: false,
      points: [],
      polylines: [],
      markers: [],
      labels: [],
      segDistance: [],
      totalDistance: 0,
      tempLine: null,
      followTitle: null,
      unitSystems: {
        metric: {
          conv: 1,
          incon: 1000,
          u1: '米',
          u2: '公里'
        },
        us: {
          conv: 3.2808,
          incon: 5279.856,
          u1: '英尺',
          u2: '英里'
        }
      },
      _zoomDisabled: false
    };
  },
  mounted() {
    this.createStyles();
  },
  beforeUnmount() {
    this.close();
  },
  methods: {
    // 切换测距模式
    toggleMeasure() {
      if (this.isOpen) {
        this.close();
      } else {
        this.open();
      }
    },
    // 创建自定义样式
    createStyles() {
      if (!document.getElementById('distance-tool-styles')) {
        const style = document.createElement('style');
        style.id = 'distance-tool-styles';
        style.innerHTML = `
          .distance-label {
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            white-space: nowrap;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
          }
          .distance-total {
            color: #ff6319;
            font-weight: bold;
          }
          .distance-close-btn {
            cursor: pointer;
            margin-left: 8px;
            color: #999;
          }
          .distance-close-btn:hover {
            color: #333;
          }
          .distance-tool-controls {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
          }
          .distance-tool-btn {
            padding: 6px 12px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
          }
        `;
        document.head.appendChild(style);
      }
    },
    // 开启测距模式
    open() {
      if (this.isOpen || !this.mapInstance) return;

      this.isOpen = true;
      this.initData();

      // 设置鼠标样式
      this.mapInstance.getContainer().style.cursor = this.cursor;

      // 创建跟随鼠标的提示标签
      this.followTitle = L.tooltip({
        permanent: true,
        direction: 'top',
        className: 'distance-label'
      }).setContent('单击确定起点');

      // 绑定地图事件
      this.mapInstance.on('click', this.handleClick);
      this.mapInstance.on('mousemove', this.handleMouseMove);
      this.mapInstance.on('dblclick', this.handleDblClick);

      // 禁用地图双击缩放，避免与测距工具冲突
      if (this.mapInstance.doubleClickZoom.enabled()) {
        this.mapInstance.doubleClickZoom.disable();
        this._zoomDisabled = true;
      }

      this.$emit('opened');
    },
    // 关闭测距模式
    close() {
      if (!this.isOpen || !this.mapInstance) return;

      this.isOpen = false;

      // 解绑地图事件
      this.mapInstance.off('click', this.handleClick);
      this.mapInstance.off('mousemove', this.handleMouseMove);
      this.mapInstance.off('dblclick', this.handleDblClick);

      // 如果临时线存在则移除
      if (this.tempLine) {
        this.mapInstance.removeLayer(this.tempLine);
        this.tempLine = null;
      }

      // 如果跟随提示存在则移除
      if (this.followTitle && this.mapInstance.hasLayer(this.followTitle)) {
        this.mapInstance.removeLayer(this.followTitle);
      }

      // 恢复地图默认鼠标样式
      this.mapInstance.getContainer().style.cursor = '';

      // 恢复地图双击缩放
      if (this._zoomDisabled) {
        this.mapInstance.doubleClickZoom.enable();
        this._zoomDisabled = false;
      }

      this.$emit('closed');

      // 如果点数少于2，清除所有测距数据
      if (this.points.length < 2) {
        this.clearAll();
      } else {
        // 测距完成，处理最后的标记和总距离显示
        this.processLastOperation();
      }
    },
    // 初始化数据
    initData() {
      this.points = [];
      this.polylines = [];
      this.markers = [];
      this.labels = [];
      this.segDistance = [];
      this.totalDistance = 0;
      this.tempLine = null;
    },
    // 清除所有测距数据
    clearAll() {
      // 清除所有线段
      this.polylines.forEach(line => {
        this.mapInstance.removeLayer(line);
      });

      // 清除所有标记点
      this.markers.forEach(marker => {
        this.mapInstance.removeLayer(marker);
      });

      // 清除所有距离标签
      this.labels.forEach(label => {
        this.mapInstance.removeLayer(label);
      });

      this.initData();
    },
    // 处理地图点击事件
    handleClick(e) {
      if (!this.isOpen) return;

      const clickedPoint = e.latlng;

      // 检查与上一个点的距离，如果太近则忽略（防止误点）
      if (this.points.length > 0) {
        const lastPoint = this.points[this.points.length - 1];
        const pixelDist = this.mapInstance.latLngToContainerPoint(lastPoint)
            .distanceTo(this.mapInstance.latLngToContainerPoint(clickedPoint));
        if (pixelDist < 5) return;
      }

      this.points.push(clickedPoint);

      // 添加节点标记
      this.addMarker(clickedPoint);

      // 如果是第一个点，则更新跟随提示的内容
      if (this.points.length === 1) {
        this.followTitle.setContent(this.followText);
      }

      // 如果已经有一个点了，创建线段
      if (this.points.length > 1) {
        const lastPoint = this.points[this.points.length - 2];
        const newLine = L.polyline([lastPoint, clickedPoint], {
          color: this.lineColor,
          weight: this.lineStroke,
          opacity: this.opacity,
          dashArray: this.lineStyle === 'dashed' ? '5, 10' : null
        }).addTo(this.mapInstance);

        this.polylines.push(newLine);

        // 计算该段距离
        const distance = this.mapInstance.distance(lastPoint, clickedPoint);
        this.segDistance.push(distance);
        this.totalDistance += distance;

        // 添加距离标签
        this.addDistanceLabel(clickedPoint, distance);
      } else {
        // 第一个点添加起点标签
        this.addDistanceLabel(clickedPoint, 0, true);
      }

      // 创建或更新临时线段（跟随鼠标）
      if (this.tempLine) {
        this.mapInstance.removeLayer(this.tempLine);
      }

      this.tempLine = L.polyline([clickedPoint, clickedPoint], {
        color: this.lineColor,
        weight: this.lineStroke,
        opacity: this.opacity / 2,
        dashArray: this.lineStyle === 'dashed' ? '5, 10' : null
      }).addTo(this.mapInstance);

      this.$emit('addpoint', {
        point: clickedPoint,
        index: this.points.length - 1,
        distance: this.totalDistance
      });
    },
    // 处理鼠标移动事件
    handleMouseMove(e) {
      if (!this.isOpen) return;

      // 更新跟随提示的位置
      if (this.followTitle) {
        this.followTitle.setLatLng(e.latlng);

        if (!this.mapInstance.hasLayer(this.followTitle)) {
          this.followTitle.addTo(this.mapInstance);
        }
      }

      // 更新临时线段的终点为当前鼠标位置
      if (this.tempLine && this.points.length > 0) {
        const lastPoint = this.points[this.points.length - 1];
        this.tempLine.setLatLngs([lastPoint, e.latlng]);

        // 计算并更新临时总距离
        const tempDis = this.mapInstance.distance(lastPoint, e.latlng);
        const totalDis = this.totalDistance + tempDis;

        // 更新跟随提示内容，显示临时总距离
        if (this.followTitle) {
          const disStr = this.formatDistance(totalDis);
          this.followTitle.setContent(`总长：<span class="distance-total">${disStr}</span><br>${this.followText}`);
        }
      }
    },
    // 处理双击事件，结束测距
    handleDblClick(e) {
      if (!this.isOpen) return;

      // 阻止事件冒泡，避免缩放地图
      L.DomEvent.stopPropagation(e);
      L.DomEvent.preventDefault(e);

      // 发出测距结束事件
      this.$emit('drawend', {
        points: this.points.slice(),
        distance: this.totalDistance,
        overlays: this.polylines.slice()
      });

      this.close();
    },
    // 添加标记点
    addMarker(latlng) {
      const markerIcon = L.divIcon({
        className: 'distance-node-icon',
        html: `<div style="width:8px;height:8px;background:${this.lineColor};border-radius:50%;border:2px solid white;"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
      });

      const marker = L.marker(latlng, {
        icon: markerIcon,
        draggable: false
      }).addTo(this.mapInstance);

      this.markers.push(marker);
      return marker;
    },
    // 添加距离标签
    addDistanceLabel(latlng, distance, isStart = false) {
      const content = isStart ? '起点' : this.formatDistance(distance);

      const label = L.tooltip({
        permanent: true,
        direction: 'top',
        className: 'distance-label',
        offset: [0, -5]
      })
          .setLatLng(latlng)
          .setContent(content)
          .addTo(this.mapInstance);

      this.labels.push(label);
      return label;
    },
    // 格式化距离显示
    formatDistance(distance) {
      const unitSystem = this.unitSystems[this.unit];
      let dis = distance * unitSystem.conv;
      let unit = unitSystem.u1;

      if (dis > unitSystem.incon) {
        dis = dis / unitSystem.incon;
        unit = unitSystem.u2;
        dis = dis.toFixed(1);
      } else {
        dis = dis.toFixed(0);
      }

      return `${dis} ${unit}`;
    },
    // 处理测距结束操作
    processLastOperation() {
      if (this.points.length < 2) return;

      // 移除临时线段
      if (this.tempLine) {
        this.mapInstance.removeLayer(this.tempLine);
        this.tempLine = null;
      }

      // 在最后一个点添加总距离标签
      const lastPoint = this.points[this.points.length - 1];

      // 使用自定义的标记而不是tooltip
      const customIcon = L.divIcon({
        className: 'distance-total-label',
        html: `
      <div class="distance-label" style="z-index: 1000;">
        总长：<span class="distance-total">${this.formatDistance(this.totalDistance)}</span>
        <span class="distance-close-btn" title="清除本次测距">×</span>
      </div>
    `,
        iconSize: [120, 40],
        iconAnchor: [60, 30]
      });

      const totalMarker = L.marker(lastPoint, {
        icon: customIcon,
        interactive: true,
        zIndexOffset: 1000
      }).addTo(this.mapInstance);

      this.markers.push(totalMarker);

      // 直接使用Leaflet的事件处理工具
      setTimeout(() => {
        const markerElement = totalMarker.getElement();
        if (markerElement) {
          const closeBtn = markerElement.querySelector('.distance-close-btn');
          if (closeBtn) {
            // 使用Leaflet的DomEvent来处理点击事件
            L.DomEvent.on(closeBtn, 'click', (e) => {
              L.DomEvent.stopPropagation(e);
              L.DomEvent.preventDefault(e);
              this.clearAll();
              this.$emit('removepolyline');
            });

            // 禁用此元素上的地图点击事件传播
            L.DomEvent.disableClickPropagation(closeBtn);
          }
        }
      }, 100);
    }
  }
};
</script>

<style scoped>
.leaflet-distance-tool-container {
  position: relative;
  z-index: 1000;
}
</style>
