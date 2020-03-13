<template>
  <v-container class="view-container">

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>
    <div class="" v-if="!isLoading">
      <v-row justify="center">
        <v-col lg="8" class="pt-0 pb-0">
          <div class="view-header">
            <h1>Terms of Use</h1>
          </div>
          <v-card class="profile-card" flat>
            <v-container class="">
              <v-card-text>
                <terms-of-use></terms-of-use>
              </v-card-text>
            </v-container>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import TermsOfUse from '@/components/auth/TermsOfUse.vue'
import Vue from 'vue'

@Component({
  components: {
    TermsOfUse
  }
})
export default class TermsOfServiceView extends Vue {
  private isLoading: boolean = false
}
</script>

<style lang="scss" scoped>
</style>
