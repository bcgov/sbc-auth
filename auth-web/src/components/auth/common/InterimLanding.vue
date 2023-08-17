<template>
  <v-container>
    <v-row justify="center">
      <v-col
        cols="12"
        lg="8"
        class="text-center"
      >
        <v-icon
          size="48"
          :color="iconColor"
          class="mb-6"
        >
          {{ icon }}
        </v-icon>
        <h1 class="mb-5">
          {{ summary }}
        </h1>
        <p class="mb-9">
          <slot name="description">
            {{ description }}
          </slot>
        </p>
        <slot name="actions">
          <v-btn
            v-if="showHomePageBtn"
            large
            link
            color="primary"
            @click="goHome()"
          >
            {{ $t('homeBtnLabel') }}
          </v-btn>
        </slot>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class InterimLanding extends Vue {
  @Prop({ default: '' }) summary: string
  @Prop({ default: '' }) description: string
  @Prop({ default: 'mdi-information-outline' }) icon: string
  @Prop({ default: 'primary' }) iconColor: string
  @Prop({ default: true }) showHomePageBtn: boolean

  goHome () {
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
