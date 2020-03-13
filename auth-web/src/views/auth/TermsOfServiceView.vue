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
            <v-container class="pa-4 pt-8">
              <v-card-text id="scroll-target" data-test="scroll-area" class="scrollable-area">
                <div v-scroll:#scroll-target="onScroll">
                  <terms-of-use></terms-of-use>
                </div>
              </v-card-text>
              <v-card-actions class="justify-center pb-4">
                <v-btn
                  large
                  depressed
                  color="primary"
                  class="font-weight-bold mx-3 px-8"
                  :disabled="!atBottom"
                  @click="clickAccepted"
                  data-test="accept-button"
                >
                  Accept Terms
                </v-btn>
                <v-btn
                  large
                  depressed
                  color="primary"
                  class="font-weight-bold mx-3 px-8"
                  @click="clickDecline"
                  data-test="decline-button"
                >
                  Decline
                </v-btn>
              </v-card-actions>
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
  private atBottom = false

  private onScroll (e) {
    this.atBottom = (e.target.scrollHeight - e.target.scrollTop) <= (e.target.offsetHeight + 25)
  }

  private clickAccepted () {
    // eslint-disable-next-line no-console
    console.log('clickAccepted')
  }

  private clickDecline () {
    // eslint-disable-next-line no-console
    console.log('clickDecline')
  }
}
</script>

<style lang="scss" scoped>
.terms-action-btn {
  font-weight: 700;
  margin: auto 12px;
}
.scrollable-area {
  height: calc(100vh - 400px);
  overflow: auto;
  padding: 0;
}
</style>
