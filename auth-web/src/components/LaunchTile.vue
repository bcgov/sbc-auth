<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { LaunchTileConfigIF } from '@/models/common'

export default defineComponent({
  name: 'LaunchTile',
  props: {
    tileConfig: {
      type: Object as () => LaunchTileConfigIF,
      required: true
    }
  },
  setup (props) {
    const localVars = (reactive({
      tileUrl: computed(() => {
        return props.tileConfig?.href ? new URL(props.tileConfig.href, import.meta.url) : null
      }),
      imgUrl: computed(() => new URL(`/src/assets/img/${props.tileConfig.image}`, import.meta.url))
    }))

    return {
      ...toRefs(localVars)
    }
  }
})
</script>

<template>
  <v-card
    v-if="tileConfig.showTile"
    class="launch-card"
  >
    <v-row>
      <v-col cols="auto">
        <img
          :src="imgUrl"
          alt=""
          class="launch-image"
        >
      </v-col>
      <v-col>
        <header>
          <h2>{{ tileConfig.title }}</h2>
          <p class="my-3">
            {{ tileConfig.description }}
          </p>
        </header>
        <v-btn
          id="tile-btn"
          class="mt-1"
          color="primary"
          filled
          dark
          large
          :href="tileUrl"
          @click="!tileConfig.href ? tileConfig.action() : null"
        >
          <span>
            {{ tileConfig.actionLabel }}
            <v-icon>mdi-chevron-right</v-icon>
          </span>
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>

<style lang="scss" scoped>
.launch-card {
  height: 225px;
  padding: 14px 26px;
}
.launch-image {
  width: 50px;
  height: auto;
}
</style>
