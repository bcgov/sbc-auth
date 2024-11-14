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
      tileUrl: computed((): string => {
        return props.tileConfig?.href ? new URL(props.tileConfig?.href, import.meta.url).toString() : null
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
    <v-row
      noGutters
      class="tile-content"
    >
      <v-col cols="2">
        <img
          :src="imgUrl"
          alt=""
          class="launch-image"
        >
      </v-col>
      <v-col class="pl-0">
        <h2>{{ tileConfig.title }}</h2>
        <p class="my-3">
          {{ tileConfig.description }}
        </p>
      </v-col>
    </v-row>

    <v-row
      noGutters
      class="mt-2"
    >
      <v-col cols="2" />
      <v-col class="ml-0">
        <v-btn
          id="tile-btn"
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
  height: 100%;
  padding: 30px;
}
.launch-image {
  width: 50px;
  height: auto;
}
.tile-content  {
  height: 70%;
}
</style>
