<template>
  <div>
    <v-tooltip bottom color="grey darken-4">
      <template v-slot:activator="{ on }">
        <v-checkbox
          color="primary"
          class="terms-checkbox ma-0 pa-0"
          hide-details
          v-model="termsAccepted"
          v-on:change="emitTermsAcceptanceStatus"
          v-on="on"
          :disabled="!canCheckTerms"
          required
        >
          <template v-slot:label>
            <span>I have read and agreed to the</span>
            <v-btn
              text
              color="primary"
              class="terms-checkbox-label-btn"
              @click.stop="openDialog()"
              data-test="terms-of-use-checkbox"
              v-on="on"
            >
              Terms of Use
            </v-btn>
          </template>
        </v-checkbox>
        <v-dialog scrollable width="1024" v-model="termsDialog" :persistent="true">
          <v-card>
            <v-card-title>
              <h2>Terms of Use</h2>
              <v-btn
                large
                icon
                @click="closeDialog"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-card-text id="scroll-target" data-test="scroll-area">
              <div v-scroll:#scroll-target="onScroll" style="height: 2000px;">
                <TermsOfUse
                  :tosType="tosType"
                ></TermsOfUse>
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
                Close
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </template>
      <span>{{tooltipTxt}}</span>
    </v-tooltip>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { User } from '@/models/user'
import documentService from '@/services/document.services.ts'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    TermsOfUse
  },
  computed: {
    ...mapState('user', [
      'userHasToAcceptTOS'
    ])
  }
})
export default class TermsOfUseDialog extends Vue {
  @Prop({ default: 'termsofuse' }) tosType: string
  @Prop({ default: false }) isUserTOS: boolean
  @Prop({ default: false }) isAlreadyAccepted: boolean
  protected readonly userHasToAcceptTOS!: boolean
  private termsDialog: boolean = true
  private termsAccepted: boolean = false
  private canCheckTerms: boolean = false
  private atBottom: boolean = false

  get tooltipTxt () {
    return 'Please read and agree to the Terms Of Use'
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

  // Tighten up some of the spacing between rows
  [class^='col'] {
    padding-top: 0;
    padding-bottom: 0;
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
</style>
