<template>
    <v-row>
        <v-col sm="12">
            <v-tooltip bottom>
                <template v-slot:activator="{ on }">
                    <v-checkbox v-on:change="emitStatus()" class="terms-checkbox" color="default" v-on="on"
                                v-model="termsAccepted" required on :disabled="!canCheckTerms">
                        <template v-slot:label>
                            <div class="terms-checkbox-label">
                                <span>I have read and agreed to the</span>
                                <v-btn text color="primary" class="pr-1 pl-1" @click.stop="openDialog()">
                                    Terms of Use
                                </v-btn>
                            </div>
                        </template>
                    </v-checkbox>
                </template>
                <span>{{tooltipTxt}}</span>
            </v-tooltip>
            <v-dialog scrollable width="1024" v-model="termsDialog" :persistent="true">
                <v-card>
                    <v-card-title>Terms of Use</v-card-title>
                    <v-card-text id="scroll-target">
                        <div v-scroll:#scroll-target="onScroll" style="height: 2000px;">
                            <p v-html="content" class="terms-container"></p>
                        </div>
                    </v-card-text>
                    <v-card-actions>
                        <v-btn large depressed color="primary" class="agree-btn" :disabled="this.offsetTop < 3000"
                               @click="termsDialog = false ;termsAccepted = true ;emitStatus()">
                            <span>Agree to Terms</span>
                        </v-btn>
                        <v-btn large depressed color="primary" class="agree-btn" :disabled="this.offsetTop < 3000"
                               @click="termsDialog = false ;emitStatus()">
                            <span>Close</span>
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </v-col>
    </v-row>

</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import documentService from '@/services/document.service.ts'
import { getModule } from 'vuex-module-decorators'

  @Component({
    directives: {}
  })
export default class TermsOfServiceDialog extends Vue {
    @Prop({ default: '' })
    lastAcceptedVersion: string
    private termsDialog = false
    private offsetTop = '0'
    private termsAccepted = false
    private content: string = ''
    private version: string = ''
    private canCheckTerms: boolean = false // shud be checkable only when terms dialos is opened atleast once
    mounted () {
      // TODO may be , cache the file somewhere in session storage or so.repeated service calls are not necessary
      documentService.getTermsOfService('termsofuse').then(response => {
        this.content = response.data.content
        this.version = response.data.version_id
      })
    }

    get tooltipTxt () {
      // return !this.canCheckTerms ? 'please read and agree to the terms of use' : 'please select terms of use'
      return 'Please read and agree to the Terms Of Use'
    }

    @Watch('lastAcceptedVersion')
    onVersionChanged (val: string, oldVal: string) {
      if (val === this.version) {
        this.termsAccepted = true
        this.canCheckTerms = true
        this.emitStatus()
      }
    }

    openDialog () {
      this.termsDialog = true
      this.canCheckTerms = true
    }

    onScroll (e) {
      this.offsetTop = e.target.scrollTop
    }

    emitStatus () {
      this.$emit('termsupdated', { 'termsversion': this.version, 'istermsaccepted': this.termsAccepted })
    }
}
</script>

<style lang="scss" scoped>
    @import '../../assets/scss/theme.scss';

    // Tighten up some of the spacing between rows
    [class^="col"] {
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

        .v-btn {
            height: auto;
            margin-left: 0.1rem;
            padding: 0.2rem;
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

    // Terms and Conditions Container
    $indent-width: 3rem;

    .terms-container ::v-deep {
        article {
            padding: 2rem;
            background: $gray1;
        }

        section {
            margin-top: 2rem;
        }

        section header {
            margin-bottom: 1rem;
            color: $gray9;
            text-transform: uppercase;
            letter-spacing: -0.02rem;
            font-size: 1.125rem;
            font-weight: 700;
        }

        section header > span {
            display: inline-block;
            width: $indent-width;
        }

        section div > p {
            padding-left: $indent-width;
        }

        section p:last-child {
            margin-bottom: 0;
        }

        p {
            position: relative;
        }

        p + div {
            margin-left: $indent-width;
        }

        p > span {
            position: absolute;
            top: 0;
            left: 0;
        }
    }
</style>
