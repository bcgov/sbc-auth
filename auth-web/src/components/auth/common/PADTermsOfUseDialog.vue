<template>
  <div class="pad-terms-container">
    <div
      role="button"
      aria-label="View Terms and Conditions"
      class="pad-terms-button"
      tab-index="0"
      @click.stop="openDialog()"
      v-if="!canCheckTerms"
    >
    </div>
    <v-checkbox
      color="primary"
      class="terms-checkbox align-checkbox-label--top ma-0 pa-0"
      hide-details
      v-model="termsAccepted"
      v-on:change="emitTermsAcceptanceStatus"
      v-on="on"
      :disabled="!canCheckTerms"
      required
    >
      <template v-slot:label>
        <span>I have read, understood and agree to the <strong class="faux-link" role="button" aria-description="Read, understand and agree to the terms of conditions" tabindex="0" v-on:keyup.enter="openDialog()" @click.stop="openDialog()">terms and conditions</strong> of the Business Pre-Authorized Debit Terms and Conditions for BC Registry Services</span>
      </template>
    </v-checkbox>
    <v-dialog
      scrollable
      width="800"
      v-model="termsDialog"
      role="dialog"
      tabindex="-1"
      aria-labelled-by="dialogTitle"
      :persistent="true">
      <v-card>
        <v-card-title class="align-start">
          <h2 id="dialogTitle">Business Pre-Authorized Debit Terms and Conditions Agreement BC Registries and Online Services</h2>
          <v-btn
            large
            icon
            aria-label="Close Terms and Conditions Dialog"
            @click="closeDialog"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="py-2 px-6" id="scroll-target" data-test="scroll-area">
          <div v-scroll:#scroll-target="onScroll">
            <PADTermsOfUse
              :tosType="tosType"
            ></PADTermsOfUse>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn
            large
            color="primary"
            class="agree-btn"
            :disabled="!atBottom"
            @click="agreeToTerms"
            data-test="accept-button"
          >
            <span>Agree to Terms</span>
          </v-btn>
          <v-btn
            large
            depressed
            @click="closeDialog"
            data-test="close-button"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import PADTermsOfUse from '@/components/auth/common/PADTermsOfUse.vue'
import { User } from '@/models/user'
import documentService from '@/services/document.services.ts'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    PADTermsOfUse
  },
  computed: {
    ...mapState('user', [
      'userHasToAcceptTOS'
    ])
  }
})
export default class PADTermsOfUseDialog extends Vue {
  @Prop({ default: 'termsofuse' }) tosType: string
  @Prop({ default: false }) isUserTOS: boolean
  @Prop({ default: false }) isAlreadyAccepted: boolean
  protected readonly userHasToAcceptTOS!: boolean
  private termsDialog: boolean = true
  private termsAccepted: boolean = false
  private canCheckTerms: boolean = false
  private atBottom: boolean = false

  get tooltipTxt () {
    return 'Please read and agree to the Terms and Conditions'
  }

  private mounted () {
    this.termsDialog = false
    if (this.isUserTOS && this.userHasToAcceptTOS) {
      this.agreeToTerms()
    }
    if (this.isAlreadyAccepted) {
      this.termsAccepted = this.canCheckTerms = true
    }
  }

  @Watch('userHasToAcceptTOS', { deep: true })
  updateTermsAccepted (val, oldVal) {
    if (this.isUserTOS && val) {
      this.agreeToTerms()
    }
  }

  private openDialog () {
    this.termsDialog = true
  }

  private closeDialog () {
    this.termsDialog = false
  }

  private onScroll (e) {
    this.atBottom = (e.target.scrollHeight - e.target.scrollTop) <= (e.target.offsetHeight + 25)
  }

  private agreeToTerms () {
    this.termsDialog = false
    this.termsAccepted = true
    this.canCheckTerms = true
    this.emitTermsAcceptanceStatus()
  }

  @Emit('terms-acceptance-status')
  private emitTermsAcceptanceStatus () {
    return this.termsAccepted
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

  .pad-terms-container {
    position: relative;
  }

  .pad-terms-button {
    position: absolute;
    top: -0.5rem;
    right: -0.5rem;
    bottom: -0.5rem;
    left: -0.5rem;
    z-index: 4;
  }

  // Tighten up some of the spacing between rows
  [class^='col'] {
    padding-top: 0;
    padding-bottom: 0;
  }

  h2 {
    max-width: 45ch;
  }

  .terms-checkbox {
    pointer-events: auto !important;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }

  .terms-checkbox-label-btn {
    height: auto !important;
    padding: 0.25rem !important;
    font-size: 1rem !important;
    text-decoration: underline;
  }

  .v-card__actions {
    justify-content: center;

    .v-btn {
      width: 8rem;
    }
  }

  .terms-container ::v-deep {
    article {
      background: $gray1;
    }
  }

  .v-tooltip__content:before {
    content: ' ';
    position: absolute;
    top: -20px;
    left: 50%;
    margin-left: -10px;
    width: 20px;
    height: 20px;
    border-width: 10px 10px 10px 10px;
    border-style: solid;
    border-color: transparent transparent var(--v-grey-darken4) transparent;
  }

  .align-checkbox-label--top {
    ::v-deep {
      .v-input__slot {
        align-items: flex-start;
      }
      .v-label {
        color: var(--v-grey-darken3);
      }
    }
  }

  .v-input-checkbox {
     .v-input .v-label {
      color: var(--v-grey-darken4) !important;
    };
  }

  .faux-link {
    color: var(--v-primary-base);
    text-decoration: underline;
  }
</style>
