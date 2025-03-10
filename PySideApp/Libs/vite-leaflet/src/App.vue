<template>
  <div>
    <div class="map-controls">
      <button @click="toggleDistanceTool" :class="{ active: isDistanceActive }">
        {{ isDistanceActive ? '关闭测距' : '开启测距' }}
      </button>
    </div>

    <div ref="mapContainer" class="map-container"></div>

    <!-- 组件方式使用 -->
    <leaflet-distance-tool
        v-if="map"
        :map="map"
        :active="isDistanceActive"
        :options="distanceOptions"
        @measure-point="onMeasurePoint"
        @measure-complete="onMeasureComplete"
        @measure-clear="onMeasureClear"
        ref="distanceTool"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, toRaw } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-hotline'
import 'leaflet-rotatedmarker'
import 'leaflet.chinatmsproviders'
import './components/libs/leaflet.mapCorrection/leaflet.mapCorrection.js'
import LeafletDistanceTool from './components/LeafletDistanceTool.vue';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import {QWebChannel} from './utils/qwebchannel_vue.js'

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize:    [25, 41],
  iconAnchor:  [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize:  [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const mapContainer = ref(null);
const distanceTool = ref(null);
const map = ref(null);
const isDistanceActive = ref(false);

// 测距选项
const distanceOptions = {
  followText: '单击确定地点，双击结束',
  unit: 'metric',
  lineColor: '#ff1919',
  lineStroke: 2,
  opacity: 1.0,
  lineStyle: 'solid',
  cursor: 'crosshair'
};

// 创建一个全局桥接对象
window.vueBridge = {};

// 初始化地图
onMounted(async () => {
  setup_leafletMap();
  setupQWebChannel()
});

// 清理资源
onUnmounted(() => {
  if (map.value) {
    map.value.remove();
    map.value = null;
  }
});

function setup_leafletMap() {
  // 地图
  map.value = L.map(mapContainer.value,
      {
        attributionControl:false,  // 隐藏logo
      }
  ).setView([29.80708, 106.52285], 20);

  let sat_map = L.tileLayer.chinaProvider('GaoDe.Satellite.Map', {
  }).addTo(toRaw(map.value));
  let anno_map = L.tileLayer.chinaProvider('GaoDe.Satellite.Annotion', {
  });

  let layerControl = L.control.layers().addTo(toRaw(map.value));

  // 添加图层组到图层控件
  layerControl.addBaseLayer(sat_map, "卫星图");
  layerControl.addOverlay(anno_map, "路网");


  // latlngs是标点坐标，格式同初始化地图时的中心坐标
  let marker = L.marker([29.80708, 106.52285], {
    // rotationAngle: 45
    // icon: DefaultIcon
  }).addTo(toRaw(map.value)); //添加到地图中
}


// 切换测距工具
function toggleDistanceTool() {
  isDistanceActive.value = !isDistanceActive.value;
}

// 事件处理
function onMeasurePoint(data) {
  console.log('测距点添加:', data);
}

function onMeasureComplete(data) {
  console.log('测距完成:', data.distance);
  isDistanceActive.value = false;
  if(bridge) {
    window.vueBridge.handleDrawEnd(data.distance.toString());
  }
}

function onMeasureClear() {
  console.log('测距清除');
}

// 热力图绘制
function updateHotline(coords) {
  if (hotlineLayer) map.removeLayer(hotlineLayer)
  let hotlineLayer = L.hotline(coords, { color: 'red', weight: 5 })
  hotlineLayer.addTo(map)
}

// 设置QWebChannel连接
function setupQWebChannel() {
  // if (window.qt && window.qt.webChannelTransport) {
  if (typeof qt != 'undefined') {
    var bridge = null;
    new QWebChannel(qt.webChannelTransport, function(channel) {
      bridge = channel.objects.web_bridge;
    });
    console.log("Qt WebChannel Ready...");
    regiPythonMethod()
  } else {
    console.log("Qt WebChannel NotExist, please Refresh...");
  }
}

function regiPythonMethod() {
  // 注册所有需要从Python访问的方法
  window.vueBridge.openDistance = openDistance;
  window.vueBridge.closeDistance = closeDistance;
}

function openDistance() {
  // toggleDistanceTool();
  distanceTool.open();
}
function closeDistance() {
  // toggleDistanceTool();
  distanceTool.value?.close();
}
</script>

<style>
.map-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.map-controls button {
  padding: 5px 10px;
  margin: 5px 0;
  cursor: pointer;
}

.map-controls button.active {
  background-color: #4c8bf5;
  color: white;
}

.leaflet-control-distance-button {
  padding: 5px 10px;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}

.leaflet-control-distance-button.active {
  background-color: #4c8bf5;
  color: white;
}
</style>