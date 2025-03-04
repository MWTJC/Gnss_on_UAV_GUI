<template>
  <div>
    <div id="map" style="height: 500px;"></div>
    <div class="controls">
      <button @click="startMeasure" :disabled="!mapReady">开始测距</button>
      <button @click="stopMeasure" :disabled="!distanceToolActive">结束测距</button>
    </div>

    <!-- 使用测距工具组件 -->
    <LeafletDistanceTool
        v-if="mapReady"
        :mapInstance="map"
        :lineColor="lineColor"
        :lineStroke="lineStroke"
        :unit="unit"
        @opened="distanceToolActive = true"
        @closed="distanceToolActive = false"
        @addpoint="onAddPoint"
        @drawend="onDrawEnd"
        @removepolyline="onRemovePolyline"
        ref="distanceTool"
    />
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import LeafletDistanceTool from './components/LeafletDistanceTool.vue';

export default {
  components: {
    LeafletDistanceTool
  },
  data() {
    return {
      map: null,
      mapReady: false,
      distanceToolActive: false,
      lineColor: '#ff6319',
      lineStroke: 3,
      unit: 'metric'
    };
  },
  mounted() {
    this.initMap();
  },
  methods: {
    initMap() {
      // 初始化地图
      this.map = L.map('map').setView([39.915, 116.404], 13);

      // 添加底图
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(this.map);

      // 标记地图已准备好
      this.mapReady = true;
    },
    startMeasure() {
      if (this.mapReady && this.$refs.distanceTool) {
        this.$refs.distanceTool.open();
      }
    },
    stopMeasure() {
      if (this.mapReady && this.$refs.distanceTool) {
        this.$refs.distanceTool.close();
      }
    },
    onAddPoint(event) {
      console.log('点添加成功:', event);
    },
    onDrawEnd(event) {
      console.log('测距完成:', event);
    },
    onRemovePolyline() {
      console.log('测距线已移除');
    }
  }
};
</script>
