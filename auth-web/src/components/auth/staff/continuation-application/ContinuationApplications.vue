<template>
  <v-container
    id="continuation-applications-review"
    class="pa-0"
  >
    <header class="view-header align-center justify-space-between mt-n1 mb-4">
      <h2 class="view-header__title">
        Continuation Applications
      </h2>
    </header>

    <!-- Table Contents -->
    <ContinuationApplicationTable />
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import ContinuationApplicationTable from './ContinuationApplicationTable.vue'

@Component({
  components: {
    ContinuationApplicationTable
  }
})
export default class ContinuationApplications extends Vue {}
</script>
