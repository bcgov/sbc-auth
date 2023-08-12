<template>
  <v-card class="product-container" :href="pprUrl">
    <v-row align="center" no-gutters>
      <v-col cols="auto">
        <!-- to use a dynamic src use 'require(<path>)' -->
        <img class="product-img" :src="getImgUrl(img)" />
      </v-col>
      <v-col class="product-info" align-self="baseline">
        <h2>{{ title }}</h2>
        <p class="mt-5 mb-0">{{ text }}</p>
        <v-btn class="primary product-info__btn px-5">
          Open
          <v-icon>mdi-chevron-right</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>
<script lang="ts">
import { Component, Watch } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import Vue from 'vue'
import { namespace } from 'vuex-class'
const userModule = namespace('user')

// FUTURE: import this from shared components once built
// - this is converted statically from UserProduct.vue in bcgov/bcregistry repo
@Component({})
export default class PPRLauncher extends Vue {
  @userModule.State('currentUser') public currentUser!: KCUserProfile

  private title = ''
  private text = ''
  private img = ''

  private get pprUrl (): string {
    return ConfigHelper.getPPRWebUrl()
  }

  async getImgUrl (img) {
    return await import(`/* @vite-ignore */ @/assets/${img}`)
  }

  @Watch('currentUser', { deep: true, immediate: true })
  assignAssetContent (): void {
    const roles = this.currentUser?.roles
    switch (true) {
      case roles.includes('ppr') && roles.includes('mhr'):
        this.img = 'AssetsRegistries_dashboard.jpg'
        this.title = this.$t('assetLauncherTitle').toString()
        this.text = this.$t('assetLauncherText').toString()
        break
      case roles.includes('mhr'):
        this.img = 'ManufacturedHomeRegistry_dashboard.jpg'
        this.title = this.$t('mhrLauncherTitle').toString()
        this.text = this.$t('mhrLauncherText').toString()
        break
      default:
        this.img = 'PPR_dashboard_thumbnail_image.jpg'
        this.title = this.$t('pprLauncherTitle').toString()
        this.text = this.$t('pprLauncherText').toString()
        break
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
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
