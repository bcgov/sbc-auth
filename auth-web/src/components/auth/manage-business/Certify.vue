<template>
  <div id="certify">
    <v-checkbox
      hide-details
      :value="isCertified"
      :rules="[(v) => !!v]"
      @change="emitIsCertified($event)"
      class="certify-checkbox mt-0 pt-0"
    >
      <template slot="label">
        <span>
          <strong>{{ legalName || '[Legal Name]' }}</strong>
          certifies that they have relevant knowledge of the {{ entity }} and is authorized
          to make this filing.
        </span>
      </template>
    </v-checkbox>

    <p class="certify-clause">{{ clause }}</p>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class Certify extends Vue {
  /** Entity name. */
  @Prop({ required: true })
  readonly legalName: string

  /** Entity name. */
  @Prop({ default: 'business' })
  readonly entity: string

  /** Certify clause. */
  @Prop({ default: '' })
  readonly clause: string

  // local variable
  protected isCertified = false

  /** Emits an event to update the Is Certified prop. */
  @Emit('update:isCertified')
  private emitIsCertified (isCertified: boolean): void {}
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

// checkbox shows red on error (per its validation)
// this also set its label color to red
.certify-checkbox.error--text {
  .certify-stmt {
    color: var(--v-error-base);
    caret-color: var(--v-error-base);
  }
}

::v-deep .v-input--checkbox {
  // align checkbox with top of its label
  .v-input__slot {
    align-items: flex-start;
  }

  // override label size and color
  .v-label {
    font-size: $px-14 !important;
    color: $gray9 !important;
  }
}

.certify-clause {
  margin: 0;
  padding-top: 1rem;
  padding-left: 2rem;
  line-height: 1.2rem;
  color: $gray9;
  font-size: $px-13;
}
</style>
