<template>
  <v-row>
    <v-col sm="12">
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-checkbox
            v-on:change="emitTermsAcceptanceStatus"
            v-on="on"
            class="terms-checkbox"
            color="default"
            v-model="termsAccepted"
            :disabled="!canCheckTerms"
            required
          >
            <template v-slot:label>
              <div class="terms-checkbox-label" v-on="on">
                <span>I have read and agreed to the</span>
                <v-btn
                  text
                  link
                  color="primary"
                  class="pr-1 pl-1"
                  @click.stop="openDialog()"
                  data-test="terms-of-use-checkbox"
                >Terms of Use</v-btn>
              </div>
            </template>
          </v-checkbox>
        </template>
        <span>{{tooltipTxt}}</span>
      </v-tooltip>
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
              depressed
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
              color="primary"
              class="agree-btn"
              @click="closeDialog"
              data-test="close-button"
            >
              <span>Close</span>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-col>
  </v-row>
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

.terms-checkbox-label {
  display: flex;
  align-items: center;
  margin-top: -0.1rem;

  .v-btn {
    height: auto !important;
    margin-left: 0.1rem;
    padding: 0;
    text-decoration: underline;
    font-size: 1rem;
  }
}

.v-card__actions {
  justify-content: center;

  .v-btn {
    width: 10rem;
  }
}

.terms-container ::v-deep {
  article {
    background: $gray1;
  }
}
</style>
