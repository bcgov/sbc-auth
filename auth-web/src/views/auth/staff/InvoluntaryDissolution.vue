<template>
  <v-container
    id="involuntary-dissolution"
    class="view-container"
  >
    <div class="view-header flex-column">
      <h1>
        Staff Involuntary Dissolution Batch
      </h1>
      <p class="mt-2 mb-0">
        B.C. Business Ready for D1 Dissolution: {{ businessesReadyforDissolutionNumber }}
      </p>
    </div>

    <!-- Automated Dissolution Section -->
    <section>
      <v-row>
        <v-col
          cols="12"
          lg="9"
        >
          <header>
            <h2>Automated Dissolution</h2>
            <p class="mt-2">
              You can set up a schedule to automate the involuntary dissolution process.
              The system will prioritize the oldest eligible businesses to move into D1 dissolution,
              automatically saving a list of businesses in each batch to the LAN.
              The schedule will run until there are no more businesses ready for D1 dissolution.
            </p>
          </header>
        </v-col>
      </v-row>
      <v-row>
        <v-col
          cols="12"
          lg="9"
        >
          <v-card
            id="company-summary-vcard"
            flat
            class="mt-2"
          >
            <CardHeader
              badgeText="Paused"
              icon="mdi-delete-clock"
              label="Automated Dissolution Schedule"
              :showBadge="isOnHold"
            />
            <DissolutionSchedule
              @update:onHold="isOnHold=$event"
            />
          </v-card>
        </v-col>
      </v-row>
    </section>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { CardHeader } from '@/components'
import DissolutionSchedule from '@/components/auth/staff/DissolutionSchedule.vue'
import { mapActions } from 'pinia'
import { useStaffStore } from '@/stores/staff'

@Component({
  components: {
    CardHeader,
    DissolutionSchedule
  },
  methods: {
    ...mapActions(useStaffStore,
      ['isDissolutionBatchOnHold'])
  }
})
export default class InvoluntaryDissolution extends Vue {
  readonly isDissolutionBatchOnHold!: () => boolean

  // Local vars
  isOnHold = false

  mounted (): void {
    this.isOnHold = this.isDissolutionBatchOnHold()
  }

  /**
   * The number of B.C. businesses that are ready for D1 Dissolution.
   * TODO: Change this once the BE is done.
   */
  get businessesReadyforDissolutionNumber (): number {
    return 0
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
h2 {
  font-size: 18px;
}

p {
  font-size: 16px;
}

// Tighten up some of the spacing between rows
[class^="col"] {
  padding-top: 0;
}
</style>
