<template>
  <div id="certify">
    <v-checkbox
      hide-details
      :value="isCertified"
      :rules="[(v) => !!v]"
      class="certify-checkbox mt-0 pt-0"
      @change="emitIsCertified($event)"
    >
      <template #label>
        <span>
          <strong>{{ trimmedCertifiedBy || "[Legal Name]" }}</strong> certifies that
          they have relevant knowledge of the {{ entity }} and is authorized to act
          on behalf of this business.
        </span>
      </template>
    </v-checkbox>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class Certify extends Vue {
  /** Entity name. */
  @Prop({ default: 'business' })
  readonly entity: string

  /** Certified by name. */
  @Prop({ default: '' })
  readonly certifiedBy: string

  // local variable
  protected isCertified = false

  /** The trimmed "Certified By" string (may be falsy). */
  get trimmedCertifiedBy (): string {
    // remove repeated inline whitespace, and leading/trailing whitespace
    return this.certifiedBy?.replace(/\s+/g, ' ').trim()
  }

  /** Emits an event to update the Is Certified prop. */
  @Emit('update:isCertified')
  protected emitIsCertified (): void {}
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme';

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

  // override checkbox color (unchecked, with or without error)
  .v-icon.mdi-checkbox-blank-outline {
    color: $gray6 !important;
    caret-color: $gray6 !important;
  }

  // override label size
  .v-label {
    font-size: $px-14 !important;
  }

  // override label color (without error)
  .v-label:not(.error--text) {
    color: $gray9 !important;
  }
}
</style>
