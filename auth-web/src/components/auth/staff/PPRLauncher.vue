<template>
  <v-card class="product-container" :href="pprUrl">
    <v-row align="center" no-gutters>
      <v-col cols="auto">
        <!-- to use a dynamic src use 'require(<path>)' -->
        <img class="product-img" :src="getImgUrl(img)" />
      </v-col>
      <v-col class="product-info">
        <h2>{{ title }}</h2>
        <p class="pt-3 ma-0">{{ text }}</p>
        <v-btn class="primary action-btn px-5">
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

  private getImgUrl (img) {
    const images = require.context('@/assets/img/')
    return images('./' + img)
  }

  @Watch('currentUser', { deep: true, immediate: true })
  assignAssetContent (): void {
    const roles = this.currentUser?.roles
    switch (true) {
      case roles.includes('ppr_staff') && roles.includes('mhr_staff'):
        this.img = 'AssetsRegistries_dashboard.jpg'
        this.title = this.$t('assetLauncherTitle').toString()
        this.text = this.$t('assetLauncherText').toString()
        break
      case roles.includes('mhr_staff'):
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
.action-btn {
  font-weight: 600;
  height: 40px !important;
  margin-top: 30px;
  text-transform: none;
  pointer-events: none;
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
  padding-left: 15px !important;

  p {
    color: $gray7;
    font-size: 1rem;
  }
}
</style>
