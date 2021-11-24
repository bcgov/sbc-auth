<template>
  <v-card
    :class="{ 'product-container': true, 'border-left': addBorder }"
    :href="pprUrl"
    @mouseover="addBorder = true"
    @mouseleave="addBorder = false"
  >
    <v-row align="center" no-gutters>
      <v-col cols="auto">
        <!-- to use a dynamic src use 'require(<path>)' -->
        <img class="product-img" src="@/assets/img/PPR_dashboard_thumbnail_image.jpg" />
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
import { Component } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import Vue from 'vue'

// FUTURE: import this from shared components once built
// - this is converted statically from UserProduct.vue in bcgov/bcregistry repo
@Component({})
export default class PPRLauncher extends Vue {
  private addBorder = false
  private text = 'Register or search for legal claims on personal property.'
  private title = 'Staff Personal Property Registry'

  private get pprUrl (): string {
    return ConfigHelper.getPPRWebUrl()
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
.border-left {
  border-left: 3px solid $app-blue !important;
}
.product-container {
  border-left: 3px solid transparent;
  box-shadow: none;
  cursor: pointer;
  height: 100%;
  max-width: none;
  padding: 30px;
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
