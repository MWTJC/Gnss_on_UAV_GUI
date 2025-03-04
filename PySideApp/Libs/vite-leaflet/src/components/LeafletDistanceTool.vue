<template>
  <div class="leaflet-distance-tool">
    <slot></slot>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onUnmounted, watch } from 'vue'
import DistanceTool from './DistanceTool'

export default defineComponent({
  name: 'LeafletDistanceTool',

  props: {
    map: {
      type: Object,
      required: true
    },
    active: {
      type: Boolean,
      default: false
    },
    options: {
      type: Object,
      default: () => ({})
    }
  },

  emits: ['measure-start', 'measure-point', 'measure-complete', 'measure-clear'],

  setup(props, { emit }) {
    const distanceTool = ref(null)

    // 监听开关状态
    watch(() => props.active, (newVal) => {
      if (distanceTool.value) {
        if (newVal) {
          distanceTool.value.open()
        } else {
          distanceTool.value.close()
        }
      }
    })

    onMounted(() => {
      // 创建测距工具
      distanceTool.value = new DistanceTool(props.map, props.options)

      // 监听事件
      distanceTool.value.addEventListener('onaddpoint', (data) => {
        emit('measure-point', data)
      })

      distanceTool.value.addEventListener('ondrawend', (data) => {
        emit('measure-complete', data)
      })

      distanceTool.value.addEventListener('onremovepolyline', () => {
        emit('measure-clear')
      })

      // 如果初始active为true，则打开测距
      if (props.active) {
        distanceTool.value.open()
      }
    })

    onUnmounted(() => {
      // 清理资源
      if (distanceTool.value) {
        distanceTool.value.close()
        distanceTool.value = null
      }
    })

    // 暴露方法
    return {
      open: () => distanceTool.value?.open(),
      close: () => distanceTool.value?.close(),
      clear: () => distanceTool.value?._clearCurData()
    }
  }
})
</script>

<style>

</style>