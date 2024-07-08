<template>
  <div id="continuation-authorization-review">
    <ModalDialog
      ref="errorDialog"
      :title="dialogTitle"
      :text="dialogText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="error"
          data-test="dialog-ok-button"
          @click="$refs.errorDialog.close()"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>

    <v-container
      v-if="!!continuationReview"
      class="view-container"
    >
      <div class="view-header flex-column">
        <h1 class="view-header__title">
          Continuation Authorization Review
        </h1>
      </div>

      <v-card
        v-if="isExpro"
        id="extraprovincial-registration-bc-vcard"
        flat
        class="mt-6"
      >
        <CardHeader
          icon="mdi-home-city-outline"
          label="Extraprovincial Registration in B.C."
        />
        <ExtraprovincialRegistrationBc :continuationReview="continuationReview" />
      </v-card>

      <v-card
        id="home-jurisdiction-information-vcard"
        flat
        class="mt-6"
      >
        <CardHeader
          icon="mdi-domain"
          label="Home Jurisdiction Information"
        />
        <HomeJurisdictionInformation :continuationReview="continuationReview" />
      </v-card>

      <!--
        *** TODO: add Continuation Authorization Review Result section here
                  and add support for View vs Review
      -->
    </v-container>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import BusinessService from '@/services/business.services'
import CardHeader from '@/components/auth/common/CardHeader.vue'
import { ContinuationReviewIF } from '@/models/continuation-review'
import ExtraprovincialRegistrationBc from '@/components/auth/staff/continuation-application/ExtraprovincialRegistrationBc.vue'
import HomeJurisdictionInformation from '@/components/auth/staff/continuation-application/HomeJurisdictionInformation.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

@Component({
  components: {
    CardHeader,
    ExtraprovincialRegistrationBc,
    HomeJurisdictionInformation,
    ModalDialog
  }
})
export default class ContinuationAuthorizationReview extends Vue {
  $refs: {
    errorDialog: InstanceType<typeof ModalDialog>
  }

  /** Review ID that comes from route. */
  @Prop({ required: true }) readonly reviewId: number

  // local variables
  dialogTitle = ''
  dialogText = ''
  continuationReview = null as ContinuationReviewIF

  get isExpro (): boolean {
    const mode = this.continuationReview?.filing?.continuationIn?.mode
    return (mode === 'EXPRO')
  }

  async mounted (): Promise<void> {
    this.continuationReview = await BusinessService.fetchContinuationReview(this.reviewId).catch(() => null)

    // check for expected data
    const review = this.continuationReview?.review
    const results = this.continuationReview?.results
    const filing = this.continuationReview?.filing

    if (!review || !results || !filing) {
      // eslint-disable-next-line no-console
      console.log('Missing data for Continuation Review =', this.continuationReview)

      this.dialogTitle = 'Unable to fetch review'
      this.dialogText = 'An error occurred while fetching the review. Please try again.'
      this.$refs.errorDialog.open()
    }
  }

  /** Prevents route changes if there's unsaved data. */
  // *** TODO: move this to review result sub-component and finish implementation?
  async beforeRouteLeave (to, from, next) {
    const haveUnsavedChanges = false
    if (haveUnsavedChanges) {
      alert('You have unsaved changes. Please cancel or submit this review instead.')
    } else {
      next()
    }
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
</style>
