<template>
  <div
    v-if="!!review && !!filing"
    id="extraprovincial-registration-bc"
  >
    <!-- Registration Number in B.C. -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Registration Number in B.C.</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="registration-number-bc">
            {{ identifier || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Registered Name in B.C. -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Registered Name in B.C.</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="registered-name-bc">
            {{ legalName || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>

    <!-- Date of Registration in B.C. -->
    <section class="section-container">
      <v-row no-gutters>
        <v-col
          cols="12"
          sm="3"
          class="pr-4"
        >
          <label>Date of Registration in B.C.</label>
        </v-col>
        <v-col
          cols="12"
          sm="9"
          class="pt-4 pt-sm-0"
        >
          <div id="registration-date-bc">
            {{ foundingDate || '[Unknown]' }}
          </div>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { ContinuationFilingIF, ContinuationReviewIF } from '@/models/continuation-review'
import DateUtils from '@/util/date-utils'

@Component({})
export default class ExtraprovincialRegistrationBc extends Vue {
  @Prop({ required: true }) readonly review: ContinuationReviewIF
  @Prop({ required: true }) readonly filing: ContinuationFilingIF

  get continuationIn () {
    return this.filing?.continuationIn
  }

  get identifier (): string {
    return this.continuationIn?.business?.identifier
  }

  get legalName (): string {
    return this.continuationIn?.business?.legalName
  }

  get foundingDate (): string {
    const date = DateUtils.apiToDate(this.continuationIn?.business?.foundingDate)
    return DateUtils.dateToPacificDate(date, true)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.section-container {
  font-size: $px-16;
  color: $gray7;
  padding: 2rem 1.5rem;

  label {
    color: $gray9;
    font-weight: bold;
  }
}

// reduce top whitespace for all articles except first one
section:not(:first-child) {
  padding-top: 1.5rem;
}

// clear bottom whitespace for all articles except last one
section:not(:last-child) {
  padding-bottom: 0;
}
</style>
