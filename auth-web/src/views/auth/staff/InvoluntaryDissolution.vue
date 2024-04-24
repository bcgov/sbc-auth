<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Staff Involuntary Dissolution Batch
      </h1>
      <p class="mt-3 mb-0">
        B.C. Business Ready for D1 Dissolution:
      </p>
    </div>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'InvoluntaryDissolution',
  setup () {
    return {}
  }
})
</script>

<style lang="scss" >
// importing FAS styles need no scope
@import '~/fas-ui/src/assets/scss/search.scss';
</style>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

</style>
