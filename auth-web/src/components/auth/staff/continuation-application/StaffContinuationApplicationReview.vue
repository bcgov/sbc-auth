<template>
  <v-container class="pa-0">
    <header class="view-header align-center justify-space-between mt-n1 mb-4">
      <h2 class="view-header__title">
        Continuation Applications
      </h2>
    </header>

    <!-- Table Contents -->
    <StaffContinuationApplicationTable />
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import StaffContinuationApplicationTable from './StaffContinuationApplicationTable.vue'

  @Component({
    components: {
      StaffContinuationApplicationTable
    }
  })
export default class StaffContinuationApplicationReview extends Vue {
}
</script>
