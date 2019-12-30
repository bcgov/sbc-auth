<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <v-icon size="48" :color="iconColor" class="mb-6">{{ icon }}</v-icon>
        <h1 class="mb-5">{{ summary }}</h1>
        <p class="mb-9"><slot name="description">{{ description }}</slot></p>
        <slot name="actions">
          <v-btn large link color="primary" @click="goHome()" v-if="showHomePageBtn">{{ $t('homeBtnLabel') }}</v-btn>
        </slot>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class InterimLanding extends Vue {
  @Prop({ default: '' }) private summary: string
  @Prop({ default: '' }) private description: string
  @Prop({ default: 'mdi-information-outline' }) private icon: string
  @Prop({ default: 'primary' }) private iconColor: string
  @Prop({ default: true }) private showHomePageBtn: boolean

  private goHome () {
    this.$router.push('/')
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .container {
    padding-top: 3rem;
    padding-bottom: 3rem;
  }
</style>
