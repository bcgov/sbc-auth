<template>
  <v-container class="pa-0">
    <header class="view-header align-center justify-space-between mt-n1 mb-4">
      <h2 class="view-header__title">
        Continuation Applications
      </h2>
    </header>

    <!-- Table Contents -->
    <StaffContinuationInTable />
  </v-container>
</template>

<script lang="ts">

import { Component, Vue } from 'vue-property-decorator'
import StaffContinuationInTable from '@/components/auth/staff/continuation-in/StaffContinuationInTable.vue'

  @Component({
    components: {
      StaffContinuationInTable
    }
  })
export default class StaffContinuationInReview extends Vue {
}
</script>
