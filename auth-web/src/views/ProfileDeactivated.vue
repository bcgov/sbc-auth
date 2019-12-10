<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <v-icon size="48" color="primary" class="mb-6">mdi-information-outline</v-icon>
        <div>
          <h1 class="mb-5">Your profile has been deactivated.</h1>
          <p class="mb-9">Your contact information, team associations and business affiliations have been removed.</p>
        </div>
        <v-btn large link color="primary" @click="goHome()">{{ $t('homeBtnLabel')}}</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import Vue from 'vue'

@Component({})
export default class ProfileDeactivated extends Vue {
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
