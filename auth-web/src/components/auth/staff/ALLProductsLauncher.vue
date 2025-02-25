<template>
  <v-card
    class="product-container"
    :href="businessURL"
  >
    <v-row
      align="center"
      no-gutters
    >
      <v-col cols="auto">
        <img
          class="product-img"
          :src="getImgUrl(img)"
        >
      </v-col>
      <v-col
        class="product-info"
        align-self="baseline"
      >
        <h2>{{ title }}</h2>
        <p class="mt-5 mb-0">
          {{ text }}
        </p>
        <v-btn class="primary product-info__btn px-5">
          Open
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import { useI18n } from 'vue-i18n-composable'

export default defineComponent({
  setup () {
    const { t } = useI18n()

    const state = reactive({
      img: 'AssetsRegistries_dashboard.jpg',
      title: t('viewAllProductsLauncherTitle').toString(),
      text: t('viewAllProductsLauncherText').toString()
    })

    const businessURL = computed(() => ConfigHelper.getBcrosDashboardURL())

    function getImgUrl (imgName: string) {
      return new URL(`/src/assets/img/${imgName}`, import.meta.url).href
    }

    return {
      ...toRefs(state),
      businessURL,
      getImgUrl
    }
  }
})
</script>

<style lang="scss" scoped>
h2 {
  line-height: 1.5rem;
}

.product-container {
  border-left: 3px solid transparent;
  box-shadow: none;
  cursor: pointer;
  height: 100%;
  max-width: none;
  padding: 30px;

  &:hover {
    border-left: 3px solid $app-blue !important;
  }
}
.product-img {
  height: 196px;
  width: 230px;
}
.product-info {
  height: 196px;
  padding-left: 15px !important;
  position: relative;

  p {
    color: $gray7;
    font-size: 1rem;
  }

  &__btn {
    font-weight: 600;
    height: 40px !important;
    text-transform: none;
    pointer-events: none;
    position: absolute;
    bottom: 0;
  }
}
</style>
